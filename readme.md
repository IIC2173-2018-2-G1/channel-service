# Channel Service
This is the channel microservice. It will be in charge of creating new channels and handling the subscriptions and de-subscriptions to channels.

This microservice uses the authentication microservice to validate requests.

# This service should allow inbound HTTP requests on port 8084

## Admitted Requests

- Get All Channels:
> GET /channels
```javascript
{}
```

> Response:
```javascript
[
    channel_object
]
```

- New Channels:
> POST /channels
```javascript
{
  "name": "string",
  "description": "string"
}
```

> Response:
```javascript
{
    channel_object
}
```

- Get Channel Info:
> GET /channels/{channel_id}
```javascript
{}
```

> Response:
```javascript
{
    channel_object
}
```

- Edit Channel Info:
> PUT /channels/{channel_id}
```javascript
{
  "name": "string",
  "description": "string"
}
```

> Response:
```javascript
{
    channel_object
}
```

# Things to note:
- Before every new message, the request must be validated