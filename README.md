# admin
`admin` application consists of next services:
- `observable`: 
scans requested directories and notifies subscribers in case of change,
- `collector`: cumulates data from `observable` instances.

## API
### `observable` methods
- `subscribe`:

    **`HTTP` method**: `POST`,

    **`URL` format**:
    ```
    http://$HOST:$PORT/subscribe?directory=$DIRECTORY&subscriber=$SUBSCRIBER
    ```
    where
    - `$HOST`: `observable` instance's host (e.g. `observable`),
    - `$PORT`: `observable` instance's port (e.g. `4092`),
    - `$DIRECTORY`: directory path for `observable` instance to scan 
    (e.g. `.` for current `observable` package directory),
    - `$SUBSCRIBER`: `subscriber` instance's URL 
    (e.g. `http://collector:4029/collect`).
    
    When
    - one of the query parameters is absent,
    - same subscription sent more than once
    
    `400 Bad Request` is returned with `JSON` object in body.

### `collector` methods
- `collect`

    **`HTTP` method**: `POST`,

    **format**:
    ```
    http://$HOST:$PORT/collect
    ```
    where
    - `$HOST`: `collector` instance's host (e.g. `collector`),
    - `$PORT`: `collector` instance's port (e.g. `4029`),
    
    **body**: `application/json`
    ```
    {
        "diff": {...,
                 $FILE_PATH: {"size": $FILE_SIZE,
                              "type": $MODIFICATION_TYPE},
                ...},
        "name": $INSTANCE_NAME
    }
    ```
    where
    - `$FILE_PATH`: modified file absolute path 
    (e.g. `"/opt/observable/observable.log"`),
    - `$FILE_SIZE`: modified file size in bytes 
    (e.g. `24043`),
    - `$MODIFICATION_TYPE`: file modification type 
    (possible values: `created`, `deleted`, `modified`),
    - `$INSTANCE_NAME`: `observable` instance name.

## Requirements
- `Docker` ([installation guide](https://docs.docker.com/engine/installation/))
- `Docker Compose` ([installation guide](https://docs.docker.com/compose/install/))

## Running with Docker Compose
We can specify `observable` instances for subscribing 
right after the `collector` instance start in `command` part 
of `collector` service definition in `docker-compose.yml`
```yaml
...
    command:
      - run
      - 'http://observable:4092/subscribe?directory=.'
...
```

Run `Docker` container
```bash
docker-compose up
```

Also we can subscribe `collector` instance after start using `curl`
```bash
curl -X POST "http://localhost:4092/subscribe?directory=.&subscriber=http://collector:4029/collect"
```

## Development with Docker Compose
Run `Docker` container with remote debugger
```bash
./set-dockerhost.sh docker-compose -f docker-compose.debug.yml up
```
