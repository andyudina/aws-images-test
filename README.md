## Test project for aws-hosted image service

### Goal
Test AWS API-GW / Lamda / KMS capabilities

### What can it do
Serves encrypted image from /image/s3-bucket-image-key endpoint.
Stores arbitrary test encrypted image in S3 bucket [see upload_image management command](https://github.com/andyudina/aws-images-test/blob/master/aws_test/apps/setup/management/commands/upload_image.py)
Image is encrypted with pgp. PGP private key itself is encrypted by AES and stored in another S3 bucket. [see setup_keys management commands](https://github.com/andyudina/aws-images-test/blob/master/aws_test/apps/setup/management/commands/setup_keys.py)
On endpoint request we decrypt pgp key, get enrypted image from s3 bucket, decrypt it with key and then return its to client.
[See AWS Lambda handler](https://github.com/andyudina/aws-images-test/blob/master/aws_image_lambda/handler.py)

### Infrastructure tips
- API is hosted with AWS API Gateaway service
- On endpoint request AWS Lambda is fired with all decryption logic
- Image is stored in S3 bucket
- AWS KMS is used for key management

### Roadmap
+ Encrypt image with PGP and store in S3
+ Encrypt PGP key by KMS key and store in anither S3 bucket
+ Lambda for endpoint
- Set up API-GW and deploy lamda
- Write usage HOW-TO
- Setuo architecture with Terraform
- Find or write reliable install tools
- Build pipeline for building (custom) C modules

## AWS Tips
Use Content-Type and Accept headers to get binary data:
curl --request GET -H "Accept: image/jpeg" -H "Content-Type: image/jpeg" https://9os3hi1h6c.execute-api.eu-central-1.amazonaws.com/SafeImage/image/image-YVHJMQXU7J  > test.jpeg

To create policy user must be in trusted relationships of role for which the policy is created
