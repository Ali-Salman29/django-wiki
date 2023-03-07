"""
A management command to update formus sites
"""
import logging
import json

from django.core.management.base import BaseCommand
from wiki.models import URLPath
from openedx.features.edly.models import EdlySubOrganization

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Update Forums Sites'

    def add_arguments(self, parser):
        """
        Add arguments for email list and date for reports.
        """
        parser.add_argument(
            '--apply',
            '-a',
            default=False,
            action='store_true',
            help='Update Database',
        )

    def update_forums_sites(self, apply=False):
        """
        Updates URLPaths based on EdlySubOrganizations
        Arguments:
            apply: Only update database when apply is set to True
        """
        updated_entries = {
            'SUCCESS': [],
            'FAILED': [],
        }
        url_paths = URLPath.objects.filter(site__domain='example.com')
        for url_path in url_paths:
            try:
                edx_org_slug = url_path.slug.split('.')[0]
                edly_org = EdlySubOrganization.objects.get(slug=edx_org_slug)
                updated_entries['SUCCESS'].append({
                    'id': url_path.id,
                    'slug': url_path.slug,
                    'partent_id': url_path.parent.id if url_path.parent else None,
                    'previous_site': str(url_path.site),
                    'updated_site': str(edly_org.lms_site),
                    
                })
                if apply:
                    url_path.site = edly_org.lms_site
                    url_path.save()
            except Exception as e:
                updated_entries['FAILED'].append({
                    'id': url_path.id,
                    'slug': url_path.slug,
                    'partent_id': url_path.parent.id if url_path.parent else None,
                    'previous_site': str(url_path.site),
                    'error': str(e),
                })
        logger.info(json.dumps(updated_entries, indent=4))
        if apply:
            logger.info("Entries Updated: {}".format(len(updated_entries['SUCCESS'])))
            logger.info("Entries Faild: {}".format(len(updated_entries['FAILED'])))
        else:
            logger.info("Database is not yet updated, send --apply flag with this command to update the database")

    def handle(self, **options):
        apply = options.get('apply', False)
        self.update_forums_sites(apply)
