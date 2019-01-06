#!/usr/bin/env bats

@test "start spinal server" {
    python3 -m coverage run -a ./server.py &
}

@test "test signature" {
    run python3 -c "import server; s = server.create_security_token(server.app.args.private_key, '1234'); r = server.verify_security_token(server.app.args.private_key, '1234', s); print(r)"
    echo "$output"
    [ "$output" == "True" ]
}


@test "stop spinal server" {
    pid=$(ps -ef | grep "coverage run -a ./server.py" | grep -v grep | awk -F\  '{print $2}')
    kill "$pid"
}
