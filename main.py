from bing_image_scraper import BingImageScraper

queries = [row.strip().lower() for row in open('./queries.txt', 'r')]

scraper = BingImageScraper()

for query in queries:
  scraper.start(
      query,
      limit=100,
      output_dir='data',
      adult_filter_on=True,
      overwrite=False
  )

