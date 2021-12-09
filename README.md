[Application] AccessKeyChecker 
===

> # Architecture
![Arch accesskeychecker](../img/accesskeychecker.png)

### AWS Service
- AWS Lambda
- AWS EventBridge

### AWS Lambda
- Application 구동 서비스

### AWS EventBridge
- 스케줄링 서비스

### Application
- AWS SDK를 통해 생성된 IAM User, IAM User AccessKey, AccessKey Active Status 조회
- WebHook을 통해 Slack 알람구성

> # Application info

### 작업프로세스
1. 계정을 운영하는 환경의 권한을 획득한다.
2. AWS 계정의 IAM User 리스트를 만든다.
3. 생성한 IAM User들 중 발급한 Active AccessKey가 90일 이상된 AccessKey 리스트를 만든다.
4. 90일 이상된 AccessKey를 비활성화 한다.
5. 90일 이상된 AccessKey를 삭제 한다.
6. 삭제 내역을 Slack를 통해 관리자에게 알린다.
7. AWS EventBridge에 등록된 스케줄을 통해 매일 (UTC)00:00:00에 Application이 구동된다.

> # Application install
### 개발환경
- OS: macOS
- Serverless Framework
- pyhon3.8, pip
- awscli

### install

```bash
~ $ pip install aws-cli
~ $ {pakcage manager: apt-get, apk, brew,..} install npm
~ $ npm install serverless -g
~ $ severless deploy --stage {stage: ControlTower} --aws-profile {aws-profile: ControlTower-role-aws-profile-name}
```

> # Reference
- [Serverless Framework docs](https://www.serverless.com/framework/docs/providers/aws/guide/)
- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/index.html)
- [Boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [Sending messages using Incoming Webhooks](https://api.slack.com/messaging/webhooks)
- [(AWS Q&A)Webhook를 사용하여 Amazon SNS 메시지를 Amazon Chime, Slack 또는 Microsoft Teams에 게시하려면 어떻게 해야 합니까?](https://aws.amazon.com/ko/premiumsupport/knowledge-center/sns-lambda-webhooks-chime-slack-teams/)
- [github(sns-to-slack.py)](https://gist.github.com/hayd/234c3097f607a32f217178322bdf4e75)
- [[Blog] Running cron jobs on AWS Lambda with Scheduled Events](https://eqolot.com/technologie/blog/running-cron-jobs-on-aws-lambda-with-scheduled-events)
- [(AWS Q&A)Lambda 함수가 다른 AWS 계정의 IAM 역할을 수임하도록 구성하려면 어떻게 해야 합니까?](https://aws.amazon.com/ko/premiumsupport/knowledge-center/lambda-function-assume-iam-role/)
