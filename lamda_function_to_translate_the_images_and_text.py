import boto3
import json

#Translate the Text and Images from Input S3 Bucket and store in to Output S3 Bucket by usin AWS Translation Service

s3_client = boto3.client('s3')
rekognition_client = boto3.client('rekognition')
translate_client = boto3.client('translate')


def translate_text(text, lang_code):
    result = translate_client.translate_text(
        Text=text,
        SourceLanguageCode='auto',
        TargetLanguageCode=lang_code
    )
    return result['TranslatedText']


def lambda_handler(event, context):

    input_bucket = event['Records'][0]['s3']['bucket']['name']
    input_key = event['Records'][0]['s3']['object']['key']

    # check if input file is an image file
    if input_key.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
  
        response = rekognition_client.detect_text(Image={'S3Object':{'Bucket':input_bucket,'Name':input_key}})
        recognized_text = ''
        for text in response['TextDetections']:
            if text['Type'] == 'LINE':
                recognized_text += text['DetectedText'] + '\n'
    else:
 
        response = s3_client.get_object(Bucket=input_bucket, Key=input_key) 
        recognized_text = ''
        for line in response["Body"].read().splitlines():
            each_line = line.decode('utf-8')
            if(each_line!=''):
                recognized_text += each_line + '\n'

   
    translated_text = translate_text(recognized_text, 'de')


    output_key = input_key + '.txt'
    s3_client.put_object(Body=translated_text, Bucket='sai-outputdocument', Key=output_key)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Translation complete!')
    }