#!/usr/bin/env bats

@test "start spinal server" {
    python3 -m coverage run -a ./spinal.py &
}

@test "stop spinal server" {
    pid=$(ps -ef | grep "coverage run -a ./spinal.py" | grep -v grep | awk -F\  '{print $2}')
    kill "$pid"
}
