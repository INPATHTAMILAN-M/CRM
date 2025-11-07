"""
Management command to create yearly targets for users using dynamic date detection
"""
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from accounts.tasks import create_targets_from_start_to_current


class Command(BaseCommand):
    help = '''Create monthly targets for users with dynamic financial/physical year detection.
    
    Uses create_targets_from_start_to_current() which automatically determines current 
    financial year (Apr-Mar) and physical year (Jan-Dec) based on today's date.
    
    Examples:
      # Current year only (default - most common use case)
      python manage.py create_yearly_targets
      
      # From specific year to current year
      python manage.py create_yearly_targets --start-fy 2020 --start-py 2020
      
      # Mixed scenario (partial historical)
      python manage.py create_yearly_targets --start-fy 2022
    '''

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-fy',
            type=int,
            help='Starting financial year (e.g., 2024 for FY 2024-25). Defaults to current FY if not provided.'
        )
        
        parser.add_argument(
            '--start-py',
            type=int,
            help='Starting physical year. Defaults to current year if not provided.'
        )
        
        parser.add_argument(
            '--default-target',
            type=float,
            default=0.00,
            help='Default target amount for users without existing UserTarget records (default: 0.00)'
        )

    def handle(self, *args, **options):
        default_target = Decimal(str(options['default_target']))
        start_fy = options.get('start_fy')
        start_py = options.get('start_py')
        
        # Display current date info for context
        from datetime import datetime
        today = datetime.now()
        current_year = today.year
        current_month = today.month
        current_fy = current_year if current_month >= 4 else current_year - 1
        
        self.stdout.write("🎯 YEARLY TARGET CREATION")
        self.stdout.write("=" * 50)
        self.stdout.write(f"📅 Current Date: {today.strftime('%Y-%m-%d')}")
        self.stdout.write(f"📅 Current Financial Year: {current_fy} (FY {current_fy}-{current_fy+1})")
        self.stdout.write(f"📅 Current Physical Year: {current_year}")
        self.stdout.write("")
        
        # Determine operation mode based on parameters
        if start_fy is None and start_py is None:
            self.stdout.write("🔹 Mode: CURRENT YEAR ONLY")
            self.stdout.write(f"   Will create targets for FY {current_fy} and PY {current_year} only")
        else:
            actual_start_fy = start_fy if start_fy is not None else current_fy
            actual_start_py = start_py if start_py is not None else current_year
            self.stdout.write("🔹 Mode: HISTORICAL TO CURRENT")
            self.stdout.write(f"   Will create targets from FY {actual_start_fy} to FY {current_fy}")
            self.stdout.write(f"   Will create targets from PY {actual_start_py} to PY {current_year}")
        
        self.stdout.write(f"💰 Default target amount: {default_target}")
        self.stdout.write("")
        
        try:
            # Use the single, smart function for all scenarios
            stats = create_targets_from_start_to_current(
                start_financial_year=start_fy,
                start_physical_year=start_py,
                default_target=default_target
            )
            
            # Display results
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS("✅ TARGET CREATION COMPLETED"))
            self.stdout.write("=" * 50)
            
            self.stdout.write(f"📊 Total users processed: {stats['total_users']}")
            self.stdout.write(f"✅ Monthly targets created: {stats['monthly_targets_created']}")
            self.stdout.write(f"📋 Monthly targets already existed: {stats['monthly_targets_existed']}")
            self.stdout.write(f"👤 User targets created: {stats['user_targets_created']}")
            
            if stats['errors']:
                self.stdout.write(self.style.WARNING(f"\n⚠️  {len(stats['errors'])} errors occurred:"))
                for error in stats['errors']:
                    self.stdout.write(self.style.ERROR(f"  - {error}"))
            else:
                self.stdout.write(self.style.SUCCESS("\n🎉 No errors occurred!"))
            
            # Summary message
            if start_fy is None and start_py is None:
                self.stdout.write(f"\n🎯 Successfully created targets for current year operations.")
            else:
                years_count = (current_fy - (start_fy or current_fy) + 1) + (current_year - (start_py or current_year) + 1)
                self.stdout.write(f"\n🎯 Successfully created historical targets spanning {years_count} year periods.")
                
        except Exception as e:
            raise CommandError(f"Failed to create targets: {str(e)}")
