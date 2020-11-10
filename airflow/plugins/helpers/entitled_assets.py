# Reference: https://github.com/aws-samples/aws-dataexchange-api-samples#python
class EntitledAssets():
	def __init__(self, data_exchange_client):
		self.data_exchange_client = data_exchange_client

	def get_dataset_info(self, dataset_id):
		return self.data_exchange_client.get_data_set(dataset_id)

	def list_dataset_revisions(self, dataset_id):
		return self.data_exchange_client.list_data_set_revisions(dataset_id)

	def get_all_dataset_asset_infos(self, dataset_id, revision_id):
		assets = []

		client = self.data_exchange_client
		res = client.list_revision_assets(DataSetId=data_set_id, RevisionId=revision_id)
		next_token = res.get('NextToken')
		
		assets += res.get('Assets')
		while next_token:
			res = client.list_revision_assets(
				DataSetId=data_set_id,
				RevisionId=revision_id,
				NextToken=next_token
			)
			assets += res.get('Assets')
			next_token = res.get('NextToken')
			
		return assets

	def export_assets(self, assets, bucket):
		asset_destinations = []
		client = self.data_exchange_client

		for asset in assets:
			asset_destinations.append({
				"AssetId": asset.get('Id'),
				"Bucket": bucket,
				"Key": asset.get('Name')
			})

		job = client.create_job(Type='EXPORT_ASSETS_TO_S3', Details={
			"ExportAssetsToS3": {
				"RevisionId": asset.get("RevisionId"), 
				"DataSetId": asset.get("DataSetId"),
				"AssetDestinations": asset_destinations
			}
		})

		job_id = job.get('Id')
		client.start_job(JobId=job_id)

		while True:
			job = client.get_job(JobId=job_id)

			if job.get('State') == 'COMPLETED':
				break
			elif job.get('State') == 'ERROR':
				raise Exception("Job {job_id} failed to complete - {message}".format(
					job_id=job_id, 
					message=job.get('Errors')[0].get('Message'))
				)

			time.sleep(60)

		return True
