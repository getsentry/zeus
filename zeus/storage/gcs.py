from datetime import timedelta
from google.cloud import storage
from io import BytesIO

from zeus.utils.functional import memoize


class GoogleCloudStorage(object):
    def __init__(self, path='', project=None, credentials=None, bucket=None):
        self.path = path
        self.bucket_name = bucket
        self.project = project
        self.credentials = credentials

    @memoize
    def client(self):
        return self.get_connection()

    @memoize
    def bucket(self):
        return self.get_bucket(self.client)

    def get_connection(self):
        return storage.Client(project=self.project, credentials=self.credentials)

    def get_bucket(self, client):
        return client.get_bucket(self.bucket_name)

    def get_file_path(self, filename):
        return '/'.join([self.path.rstrip('/'), filename])

    def delete(self, filename):
        blob = self.bucket.blob(self.get_file_path(filename))
        blob.delete()

    def save(self, filename, fp):
        blob = self.bucket.blob(self.get_file_path(filename))
        blob.upload_from_file(fp)

    def url_for(self, filename, expire=300):
        blob = self.bucket.blob(self.get_file_path(filename))
        return blob.generate_signed_url(timedelta(seconds=expire))

    def get_file(self, filename):
        blob = self.bucket.blob(self.get_file_path(filename))
        return BytesIO(blob.download_as_string())
