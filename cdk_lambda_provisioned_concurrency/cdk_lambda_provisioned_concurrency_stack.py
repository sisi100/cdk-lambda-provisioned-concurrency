from aws_cdk import core as cdk, aws_lambda, aws_applicationautoscaling as appscaling
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
        hoge_alias = aws_lambda.Alias(self, "HogeAlias", alias_name="hoge-alias", version=hoge_version)

        # エイリアスをオートスケールのターゲットに設定する
        hoge_scaling = hoge_alias.add_auto_scaling(min_capacity=1, max_capacity=5)

        # ターゲット追跡スケーリングする
        hoge_scaling.scale_on_utilization(utilization_target=0.5)  # 使用率が50%を付近になるようにする

        # スケジュールでスケーリングする
        hoge_scaling.scale_on_schedule(
            "Hoge1Schedule", schedule=appscaling.Schedule.cron(hour="0", minute="0"), max_capacity=5, min_capacity=2
        )
        hoge_scaling.scale_on_schedule(
            "Hoge2Schedule", schedule=appscaling.Schedule.cron(hour="20", minute="0"), max_capacity=1, min_capacity=1
        )
