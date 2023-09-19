from constructs import Construct
from aws_cdk import (
    Stack,
    RemovalPolicy,
    BundlingOptions,
    DockerImage,
    aws_lambda as _lambda,
    aws_ec2 as ec2,
    aws_efs as efs,
    aws_s3 as s3,
    aws_apigateway as apigw,
)


class CdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a new VPC with private subnet
        vpc = ec2.Vpc(self, "chatbot-vpc",
            max_azs=3,
            subnet_configuration=[ec2.SubnetConfiguration(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                name="Private",
                cidr_mask=24
            )]
        )

         # Create a new EFS file system
        file_system = efs.FileSystem(self, "MyEfsFileSystem",
            vpc=vpc,
            encrypted=True,
            performance_mode=efs.PerformanceMode.GENERAL_PURPOSE,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # EFS access point
        access_point = file_system.add_access_point(
            "AccessPoint",
            path="/export",
            create_acl=efs.Acl(owner_uid="1000", owner_gid="1000", permissions="750"),
            posix_user=efs.PosixUser(gid="1000", uid="1000")
        )

        bucket = s3.Bucket(
            self,
            "chatbot-bucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        #new lambda resource
        lambda_fn = _lambda.Function(
            self,
            "saveChatbotHistory",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="save_chat_history.handler",
            code=_lambda.Code.from_asset("lambda/package/save_chat_history.zip"),
            vpc=vpc,
            filesystem=_lambda.FileSystem.from_efs_access_point(access_point, "/mnt/efs"),  # Access EFS via "/mnt/efs" in the Lambda function  
            environment={
                "BUCKET_NAME": bucket.bucket_name
            }   
        )

        # Create API Gateway
        api_gateway = apigw.RestApi(
            self,
            "SaveChatbotHistory"
        )

        bot_id_resource = api_gateway.root.add_resource("{bot_id}")
        client_id_resource = bot_id_resource.add_resource("{client_id}")
        save_history_resource = client_id_resource.add_resource("save_history")
        
        post_integration = apigw.LambdaIntegration(lambda_fn)
        get_integration = apigw.LambdaIntegration(lambda_fn)
        save_history_resource.add_method("POST", post_integration)
        save_history_resource.add_method("GET", get_integration)

        bucket.grant_read_write(lambda_fn)
        vpc.add_gateway_endpoint("S3Endpoint", service=ec2.GatewayVpcEndpointAwsService.S3)
