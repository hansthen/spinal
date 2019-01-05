# spinal
The test database

Notes for testing
=================
Start testing locally:
    ssh -R 80:localhost:5000 serveo.net

Reconfigure webhooks in chargebee
    Settings --> Configure Chargebee --> API keys and webhooks --> Webhooks
    Set the webhook url to https://<code>.ngrok.io/webhooks/chargebee/0174ea35-381a-426a-8ab5-94130d6118fb

Screens still to be developed
=============================
1. Overview page of all projects registered to a user
2. Test results per project
3. Installation / integration instructions
4. Test search dashboard

https://docs.gitlab.com/ee/ci/variables/README.html
https://docs.travis-ci.com/user/environment-variables/#default-environment-variables

Signing library
===============
https://pynacl.readthedocs.io/en/stable/
