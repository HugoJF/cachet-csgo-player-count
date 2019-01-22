# Cachet CS:GO player count daemon

Daemon written in Python 3 to populate Cachet metrics with total player amount in a given server.

### DotEnv variables:
`URL` - Cachet URL.

`API_KEY` - Cachet API key.

`IP` - CS:GO server IP.

`INTERVAL` - How long to wait before querying servers again.

`METRIC_ID` - What Metric ID should be POSTed.

`UPDATE_INTERVAL` - How long to wait before querying Steam API again.