@Library("wam-pipelines") _

dockerBatch  {

    //The list of the DEV environments
    nonProdEnvs = ["dev", "qa"]

    //possible QA environments
    qaEnvs = ["qa"]

    //prod environment
    prodEnv = "scx"

    //DR docker swarm environment
    drEnv = "pasx"

    //remove the Stack every deploy.
    removeStack = "yes"

    releaseVersion = "0.1"

    templates=["conf/templates/config.ctmpl"]

    secrets=["config.json"]

    //build tool tag (python-3.6).  It is optional, if this is set, the buildSteps has to be provided.
    builderTag = "python-2-3-latest"

    //build steps, it included all the test and compile commands
    buildSteps = [
            "chmod +x test.sh",
            "./test.sh"
    ]
}