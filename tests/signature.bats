@test "signature" {
    run python3 -m coverage run -a ../signature.py generate
    echo "$output"
    key="$output"
    run python3 -m coverage run -a ../signature.py sign --key "$key" --data "The snow this year is better at Innsbrook."    
    signature="$output"
    run python3 -m coverage run -a ../signature.py verify --key "$key" --signature "$signature"
    data="$output"
    echo $data
    [ "$data" == "The snow this year is better at Innsbrook." ]
}


@test "invalid signature" {
    run python3 -m coverage run -a ../signature.py generate
    key="$output"
    run python3 -m coverage run -a ../signature.py sign --key "$key" --data "The horse is in the barn"    
    signature="$output"
    run python3 -m coverage run -a ../signature.py verify --key "$key" --signature "${signature}1213"
    [ "$status" -ne 0 ]
}
