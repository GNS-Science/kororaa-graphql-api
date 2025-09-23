# DEVELOPMENT

This applicaiton if serverless.com python.

### Environment setup

 - clone the repo
 - check/install a recent node version >=22
   `nvm use 22`

- setup python env
```
pyenv local 3.10
poetry env use 3.10
```

setup yarn 2 ...
```
corepack enable
yarn set version berry
yarn install
```

Now `yarn sls info` should print something like ...

```
chrisbc@tryharder-ubuntu:/GNSDATA/API/kororaa-graphql-api$ sls info
Running "serverless" from node_modules
Environment: darwin, node 22.16.0, framework 3.40.0 (local), plugin 7.2.3, SDK 4.5.1
Credentials: Local, "default" profile
Docs:        docs.serverless.com
Support:     forum.serverless.com
Bugs:        github.com/serverless/serverless/issue

```
You'll problably see an error, if your AWS credentials are not thise required for SLS.

## TESTING

### Run API locally
```
ENABLE_METRICS=0 poetry run yarn sls wsgi serve
```

## DEPLOY DEV service

```
AWS_PROFILE=**** poetry run yarn sls  --region ap-southeast-2 --stage dev
```

### API Feature tests
You need an environment variable set: `TESTING=1` otherwise Moto mocking for S3 is clobbered.

Using the `poetry-dotenv-plugin` you can create an .env file like so...
```
echo TESTING=1 > .env
```

then `$>poetry run pytest` should just work.





