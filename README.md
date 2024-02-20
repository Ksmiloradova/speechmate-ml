# AudioLand.DUB ML pipeline

## Install Make

#### On Linux
```shell
sudo apt update
sudo apt install build-essential
sudo apt install make
```

#### On MacOS
```shell
brew install make
```
Now we can use the `make` command


## Install Python dependencies
To install all python dependencies that we use, run this:
```shell
make install
```


## Run the application
To run the app locally with `uvicorn`, run this command:
```shell
make run
```
If you need to run the app locally for a single test, run this command:
```shell
python3 main.py
```

#### Check `main.py` arguments and endpoint call
```python
if __name__ == "__main__":
    print("main started")
    # Make sure to specify the correct arguments
    user_id = "your-user-id"
    project_id = "your-project-id"
    target_language = "your-target-language"
    original_file_location = f"{user_id}/{project_id}/test-video-1min.mp4"
    generate(project_id, target_language, original_file_location)
```


## Deploy to fly.io
To deploy the app to fly.io, run this command:
```shell
make deploy
```

### *Please note that we use Github Actions, so if you make a pull request or commit in `main`, you don't need to run the deployment command every time*
