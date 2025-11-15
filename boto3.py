class _StubS3Client:
    def get_object(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError("S3 client not available in test stub")

    def put_object(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError("S3 client not available in test stub")


def client(name):  # pragma: no cover
    if name != "s3":
        raise NotImplementedError(f"Unsupported client: {name}")
    return _StubS3Client()
