# Requirements

Use the simple protozoa setup, with just two VMs. In each VM, add the following line to /etc/hosts:
`192.168.3.100	jitsi`

When launching the chromium browser in the protozoa VMs, use an URL endpoint like this:
`https://jitsi/meeting`

# Recording

One of the participants will be given the ability to record the meeting. When finished, the meeting file can be found (in the jitsi VM) in /usr/local/eb/recordings.
Jitsi uses Jibri to record meetings - using selenium and chromium in order to join the meeting as an invisible participant and record the incoming video and audio.

## Experiments

We found that recording the meeting with an instrumented chromium always showed random giberish as the video. This didn't change whether there was only one or two participants or whether Protozoa was in use or not. We also found that Protozoa could not function while the meeting was being recorded, possibly due to there being a third participant, albeit invisble.
