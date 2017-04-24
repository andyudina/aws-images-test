## Test project for aws-hosted image service

### Goal
Test AWS API-GW / Lamda / KMS capabilities

### What can it do
Serves encrypted image from /image/s3-bucket-image-key endpoint.
Stores arbitrary test encrypted image in S3 bucket (see upload_image management command) [TODO: link here]
Image is encrypted with pgp. PGP private key itself is encrypted by AES and stored in another S3 bucket. (see setup_keys management commands) [TODO: link here]
On endpoint request we decrypt pgp key, get enrypted image from s3 bucket, decrypt it with key and then return its to client.

### Infrastructure tips
- API is hosted with AWS API Gateaway service
- On endpoint request AWS Lambda is fired with all decryption logic
- Image is stored in S3 bucket
- AWS KMS is used for key management

### Roadmap
- Encrypt image with PGP and store in S3
- Encrypt PGP key by KMS key and store in anither S3 bucket
- Lambda for endpoint 
- Set up API-GW and deploy lamda
- Write usage HOW-TO
- Setuo architecture with Terraform