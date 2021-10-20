from aws_cdk import core as cdk, aws_lambda
from datetime import datetime


class CdkLambdaProvisionedConcurrencyStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambdaを作る
        hoge_lambda = aws_lambda.Function(
            self,
            "HogeLambda",
            code=aws_lambda.Code.from_asset("src"),
            handler="index.handler",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            architecture=aws_lambda.Architecture.ARM_64,  # プロビジョニングするのでARMできるだけ安くする
        )

        # 新しいバージョンを発番する
        hoge_version = aws_lambda.Version(
            self,
            f"HogeVersion{datetime.today().timestamp()}",  # デプロイ毎にバージョンを作るためにIDを変化させる必要がある
            lambda_=hoge_lambda,
            removal_policy=cdk.RemovalPolicy.RETAIN,  # 過去バージョンを削除しないようにする
        )

        # 新しいバージョンからエイリアスを作る
        aws_lambda.Alias(
            self, "HogeAlias", alias_name="hoge-alias", version=hoge_version, provisioned_concurrent_executions=1
        )  # versionに`hoge_lambda.latest_version`を指定した場合はプロビジョニングできない
