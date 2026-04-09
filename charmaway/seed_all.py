#!/usr/bin/env python
"""Script to seed all database data from all apps."""
import os
import sys


def main():
    """Run all seeder commands."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'charmaway.settings')

    try:
        import django
        django.setup()
        from django.core.management import call_command
        from django.core.management.color import color_style
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    style = color_style()

    print(style.SUCCESS('='*60))
    print(style.SUCCESS('Starting complete database seeding...'))
    print(style.SUCCESS('='*60))

    # List of all seeders to run in order
    seeders = [
        'seed_catalog_simple',  # Using simplified seeder with new categories
        'seed_services',  # Seed services after catalog to ensure categories exist
        'seed_users',
        'seed_orders',
        # Add more seeders here as you create them:
        # 'seed_customers',
        # 'seed_reviews',
    ]

    successful = []
    failed = []

    for seeder in seeders:
        print(f'\n{"="*60}')
        print(f'Running {seeder}...')
        print(f'{"="*60}\n')

        try:
            call_command(seeder)
            successful.append(seeder)
            print(style.SUCCESS(f'✓ {seeder} completed successfully'))
        except Exception as e:
            failed.append(seeder)
            print(style.ERROR(f'✗ {seeder} failed: {str(e)}'))

    # Summary
    print(f'\n{"="*60}')
    print(style.SUCCESS('SEEDING SUMMARY'))
    print(f'{"="*60}')
    print(f'✓ Successful: {len(successful)}/{len(seeders)}')

    if successful:
        for seeder in successful:
            print(style.SUCCESS(f'  - {seeder}'))

    if failed:
        print(f'\n✗ Failed: {len(failed)}/{len(seeders)}')
        for seeder in failed:
            print(style.ERROR(f'  - {seeder}'))

    if not failed:
        print(style.SUCCESS('\n🎉 All seeders completed successfully!'))
    else:
        print(style.WARNING('\n⚠ Some seeders failed. Check the output above.'))

    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())