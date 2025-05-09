package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"time"

	"github.com/joho/godotenv"
)

type Property struct {
	Value  string `json:"value"`
	Source Source `json:"source"`
}

type Source struct {
	Type string `json:"type"`
	Data string `json:"data"`
}

type PoolList struct {
	Name       string              `json:"name"`
	State      string              `json:"state"`
	Properties map[string]Property `json:"properties"`
}

type ZpoolList struct {
	Pools map[string]PoolList `json:"pools"`
}

type ScanStats struct {
	Function string `json:"function"`
	State    string `json:"state"`
	EndTime  string `json:"end_time"`
}

type Vdev struct {
	Name           string          `json:"name"`
	VdevType       string          `json:"vdev_type"`
	State          string          `json:"state"`
	ReadErrors     string          `json:"read_errors"`
	WriteErrors    string          `json:"write_errors"`
	ChecksumErrors string          `json:"checksum_errors"`
	Vdevs          map[string]Vdev `json:"vdevs"`
}

type PoolStatus struct {
	Name       string          `json:"name"`
	State      string          `json:"state"`
	ScanStats  ScanStats       `json:"scan_stats"`
	Vdevs      map[string]Vdev `json:"vdevs"`
	ErrorCount string          `json:"error_count"`
}

type ZpoolStatus struct {
	Pools map[string]PoolStatus `json:"pools"`
}

func main() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}

	infoWebhook := os.Getenv("DISCORD_INFO_WEBHOOK")
	alertWebhook := os.Getenv("DISCORD_ALERT_WEBHOOK")
	if infoWebhook == "" || alertWebhook == "" {
		log.Fatal("DISCORD_INFO_WEBHOOK and DISCORD_ALERT_WEBHOOK must be set in .env")
	}

	cmd := exec.Command("zpool", "list", "-j")
	output, err := cmd.Output()
	if err != nil {
		log.Fatalf("Failed to run zpool list: %v", err)
	}

	var zpoolList ZpoolList
	err = json.Unmarshal(output, &zpoolList)
	if err != nil {
		log.Fatalf("Failed to parse zpool list JSON: %v", err)
	}
	if len(zpoolList.Pools) == 0 {
		log.Fatal("No pools found")
	}

	poolName := "pool_1"
	poolList, ok := zpoolList.Pools[poolName]
	if !ok {
		log.Fatalf("Pool %s not found", poolName)
	}

	capacityStr := poolList.Properties["capacity"].Value
	capacity := parsePercentage(capacityStr)

	cmd = exec.Command("zpool", "status", "-j")
	output, err = cmd.Output()
	if err != nil {
		log.Fatalf("Failed to run zpool status: %v", err)
	}

	var zpoolStatus ZpoolStatus
	err = json.Unmarshal(output, &zpoolStatus)
	if err != nil {
		log.Fatalf("Failed to parse zpool status JSON: %v", err)
	}
	poolStatus, ok := zpoolStatus.Pools[poolName]
	if !ok {
		log.Fatalf("Pool %s not found in status", poolName)
	}

	state := poolStatus.State
	scanEndTimeStr := poolStatus.ScanStats.EndTime

	scanEndTime, err := time.Parse("Mon Jan  2 03:04:05 PM MST 2006", scanEndTimeStr)
	if err != nil {
		log.Fatalf("Failed to parse scrub end time: %v", err)
	}

	monthAgo := time.Now().AddDate(0, 0, -31)
	isScrubRecent := scanEndTime.After(monthAgo)
	isCapacityOk := capacity < 80
	isStateOk := state == "ONLINE" && poolStatus.ErrorCount == "0"
	allOk := isStateOk && isCapacityOk && isScrubRecent

	var title string
	var webhook string
	var color int
	if allOk {
		title = "✅ ZFS Health Report ✅"
		webhook = infoWebhook
		color = 4378646
	} else {
		title = "🚨 ZFS Health Report -- ATTENTION!! 🚨"
		webhook = alertWebhook
		color = 14177041
	}

	stateField := map[string]string{
		"name":  "State",
		"value": state,
	}

	var capMsg string
	if isCapacityOk {
		capMsg = fmt.Sprintf(
			"Pool used capacity is **%d%%**. It is recommended to stay under 80%%",
			capacity,
		)
	} else {
		capMsg = fmt.Sprintf("**WARNING** Pool used capacity is **%d%%**. It is recommended to stay under 80%%", capacity)
	}
	poolUtilField := map[string]string{
		"name":  "Pool Utilization",
		"value": capMsg,
	}

	scanDate := scanEndTime.Format("2006-01-02")
	var scanMsg string
	if isScrubRecent {
		scanMsg = fmt.Sprintf(
			"The last scrub was on %s, which is within defined tolerance.",
			scanDate,
		)
	} else {
		scanMsg = fmt.Sprintf("The last scrub was on %s, which is **outside defined tolerance.**", scanDate)
	}
	scanField := map[string]string{
		"name":  "Scan",
		"value": scanMsg,
	}

	message := map[string]any{
		"username": "ZFSBot",
		"embeds": []map[string]any{
			{
				"color":  color,
				"title":  title,
				"fields": []map[string]string{stateField, poolUtilField, scanField},
			},
		},
	}

	jsonPayload, err := json.Marshal(message)
	if err != nil {
		log.Fatalf("Failed to marshal payload: %v", err)
	}

	resp, err := http.Post(webhook, "application/json", bytes.NewBuffer(jsonPayload))
	if err != nil {
		log.Fatalf("Failed to send to Discord: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != 204 {
		log.Printf("Discord returned status: %d", resp.StatusCode)
	}

	if allOk {
		os.Exit(0)
	} else {
		os.Exit(1)
	}
}

func parsePercentage(s string) int {
	var percent int
	_, err := fmt.Sscanf(s, "%d%%", &percent)
	if err != nil {
		log.Fatalf("Failed to parse capacity percentage: %v", err)
	}
	return percent
}
