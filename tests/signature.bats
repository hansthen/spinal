@test "test signatures" {
    run rm ./id_rsa ./id_rsa.pub
    ssh-keygen -t rsa -q -P "" -f ./id_rsa
    private_key=$(cat ./id_rsa)
    public_key=$(cat ./id_rsa.pub)
    signature=$(python3 -c "import signature; print(signature.create_security_token( \"\"\"${private_key}\"\"\", 'hello world'))")
    echo "$signature"
    echo "-----"
    result=$(python3 -c "import signature; print(signature.verify_security_token(\"\"\"${public_key}\"\"\", \"\"\"${signature}\"\"\", 'hello world'))")
    echo $result
    [ "$result" == True ]
}
