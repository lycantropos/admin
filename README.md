# admin
`admin` application consists of the next services:
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
        "source": $INSTANCE_NAME
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

- `search`

    **`HTTP` method**: `GET`,

    **format**:
    ```
    http://$HOST:$PORT/search?source=$SOURCE&dateStart=$DATE_START&dateEnd=$DATE_END&offset=$OFFSET&limit=$LIMIT
    ```
    where
    - `$HOST`: `collector` instance's host (e.g. `collector`),
    - `$PORT`: `collector` instance's port (e.g. `4029`),
    - `$SOURCE`, required: `observable` instance name,
    - `$DATE_START`, required: 
    date time string (in [`ISO 8601`](https://en.wikipedia.org/wiki/ISO_8601)
     from which obtain records (e.g. `2017-01-01T23:59:59`),
    - `$DATE_END`, required: 
    date time string (in [`ISO 8601`](https://en.wikipedia.org/wiki/ISO_8601)) 
    to which obtain records (e.g. `2018-12-31T23:59:59`),
    - `$OFFSET`, optional: records count to skip (e.g. `0`),
    - `$LIMIT`, optional: max records count to return (e. g. `100`),
    
    **response**: `application/json`
    ```
    {
        "data": {
            "diff": {...,
                     $FILE_PATH: {"size": $FILE_SIZE,
                                  "type": $MODIFICATION_TYPE},
                    ...},
            "source": $INSTANCE_NAME,
            "timestamp": $TIMESTAMP
        },
        "offset": $OFFSET,
        "count": $COUNT
    }
    ```
    where
    - `$FILE_PATH`: modified file absolute path 
    (e.g. `"/opt/observable/observable.log"`),
    - `$FILE_SIZE`: modified file size in bytes 
    (e.g. `24043`),
    - `$MODIFICATION_TYPE`: file modification type 
    (possible values: `created`, `deleted`, `modified`),
    - `$INSTANCE_NAME`: `observable` instance name 
    (e.g. `observable`),
    - `$TIMESTAMP`: record's [`Unix` timestamp](https://en.wikipedia.org/wiki/Unix_time) 
    (e.g. `1504758839`),
    - `$OFFSET`: offset from query (e.g. `0`),
    - `$COUNT`: total records count for given query (e.g. `200`).


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
