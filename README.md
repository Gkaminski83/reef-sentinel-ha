# Reef Sentinel Home Assistant Integration

## What is Reef Sentinel
Reef Sentinel is a cloud service for monitoring reef aquarium health and water chemistry. This custom integration connects Home Assistant to the Reef Sentinel API and exposes tank health, parameters, trends, and last update time as sensors.

## Installation via HACS
1. Open HACS in Home Assistant.
2. Go to **Integrations**.
3. In **Custom repositories**, paste this GitHub repository URL in HTTPS format (for example `https://github.com/<OWNER>/<REPO>`), then set category to **Integration**.
4. Search for **Reef Sentinel** and install it.
5. Restart Home Assistant.

## Setup steps
1. In Home Assistant, go to **Settings -> Devices & Services**.
2. Click **Add Integration**.
3. Search for **Reef Sentinel**.
4. Enter your Reef Sentinel API key.
5. Finish setup; sensors will be created under the **Reef Tank** device.

The integration polls the cloud API every 5 minutes (300 seconds).

## Where to get API key
1. Sign in to Reef Sentinel at `https://app.reef-sentinel.com`.
2. Open your account or integration settings.
3. Generate/copy your Home Assistant API key.
4. Paste it during integration setup.

API endpoint used by this integration:
`GET https://app.reef-sentinel.com/api/ha/tank-status` with header `X-API-Key: YOUR_API_KEY`
