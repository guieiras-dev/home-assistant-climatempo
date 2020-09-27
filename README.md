# Home Assistant Climatempo component

A Weather component that fetches current weather conditions and forecast from [Climatempo](https://climatempo.com.br).

## Installation

Copy repository content to your Home Assistant `config/custom_components` folder. You can use Samba server for instance.

## Configuration

1. Get an API key for Climatempo API. Login and create a project on https://advisor.climatempo.com.br and copy your project token.

2. Search for your locale code using http://apiadvisor.climatempo.com.br/api/v1/locale/city?name=your-city&state=your-state&token=your-project-token

3. Enable request to your locale using the following code:
```bash
curl -X PUT \
     'http://apiadvisor.climatempo.com.br/api-manager/user-token/your-project-token/locales' \
         -H 'Content-Type: application/x-www-form-urlencoded' \
         -d 'localeId[]=your-locale-code'

```

4. Add the following code to your `configuration.yaml`:

```yaml
weather:
  - platform: climatempo
    name: <whatever you want> (optional, default "weather")
    api_key: <your-project-token>
    locale: <your-locale-code>
```
