"""
Jobs Client
Integrates with abis-search project to fetch new job postings
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class JobsClient:
    def __init__(self):
        """Initialize jobs client"""
        self.abis_search_path = os.getenv('ABIS_SEARCH_PATH', '/Users/abiravindra/abis-search')

        # Criteria for matching jobs
        self.criteria = {
            'min_salary': 300000,
            'locations': ['San Francisco', 'New York', 'SF', 'NYC', 'Bay Area', 'Remote'],
            'titles': ['VP of Growth', 'VP of Demand Generation', 'Vice President of Growth', 'VP Growth']
        }

    def get_new_jobs(self, since_hours=24):
        """
        Get new job postings that match criteria

        Args:
            since_hours: Look for jobs posted in last N hours

        Returns:
            list: Matching job postings
        """
        try:
            # Read jobs data from abis-search project
            jobs_file = os.path.join(self.abis_search_path, 'jobs-data.js')

            if not os.path.exists(jobs_file):
                print(f"Jobs file not found: {jobs_file}")
                return []

            # Parse JavaScript file (basic parsing)
            with open(jobs_file, 'r') as f:
                content = f.read()

            # Extract job data (simplified - assumes specific format)
            jobs = self._parse_jobs_data(content)

            # Filter by criteria
            matching_jobs = self._filter_jobs(jobs)

            # Sort by most recent
            matching_jobs.sort(key=lambda x: x.get('posted', ''), reverse=True)

            return matching_jobs[:5]  # Return top 5 matches

        except Exception as e:
            print(f"Error fetching jobs: {e}")
            return []

    def get_target_company_updates(self):
        """
        Check for updates from target companies (Google, Meta, etc.)

        Returns:
            list: Updates from target companies
        """
        try:
            companies_file = os.path.join(self.abis_search_path, 'target-companies.js')

            if not os.path.exists(companies_file):
                return []

            with open(companies_file, 'r') as f:
                content = f.read()

            # Check for any status changes
            # This is a simplified version - in production, would track changes
            updates = []

            target_companies = ['Google', 'Meta', 'ServiceNow', 'DoorDash', 'LinkedIn']
            for company in target_companies:
                if f'status: "No VP' not in content or company in content:
                    # Placeholder for detecting actual updates
                    pass

            return updates

        except Exception as e:
            print(f"Error checking target companies: {e}")
            return []

    def _parse_jobs_data(self, content):
        """
        Parse jobs from JavaScript file

        Args:
            content: JavaScript file content

        Returns:
            list: Job objects
        """
        jobs = []

        # Extract LinkedIn jobs
        if 'linkedin: [' in content:
            linkedin_section = content.split('linkedin: [')[1].split('],')[0]
            jobs.extend(self._extract_jobs_from_section(linkedin_section, 'LinkedIn'))

        # Extract Wellfound jobs
        if 'wellfound: [' in content:
            wellfound_section = content.split('wellfound: [')[1].split('],')[0]
            jobs.extend(self._extract_jobs_from_section(wellfound_section, 'Wellfound'))

        # Extract Welcome to the Jungle jobs
        if 'jungle: [' in content:
            jungle_section = content.split('jungle: [')[1].split(']')[0]
            jobs.extend(self._extract_jobs_from_section(jungle_section, 'Welcome to the Jungle'))

        return jobs

    def _extract_jobs_from_section(self, section, source):
        """Extract individual job objects from a section"""
        jobs = []

        # Split by job objects (between { and })
        job_strings = section.split('},')

        for job_str in job_strings:
            if 'title:' in job_str:
                job = self._parse_job_object(job_str, source)
                if job:
                    jobs.append(job)

        return jobs

    def _parse_job_object(self, job_str, source):
        """Parse a single job object string"""
        try:
            job = {'source': source}

            # Extract fields using simple string parsing
            fields = ['title', 'company', 'location', 'salary', 'posted']

            for field in fields:
                if f'{field}:' in job_str:
                    value = job_str.split(f'{field}:')[1].split(',')[0].strip()
                    # Remove quotes
                    value = value.strip('"').strip("'")
                    job[field] = value

            return job

        except Exception as e:
            return None

    def _filter_jobs(self, jobs):
        """Filter jobs by criteria"""
        matching = []

        for job in jobs:
            # Check title
            title_match = any(
                title.lower() in job.get('title', '').lower()
                for title in self.criteria['titles']
            )

            # Check location
            location_match = any(
                loc.lower() in job.get('location', '').lower()
                for loc in self.criteria['locations']
            )

            # Check salary (if disclosed)
            salary_match = self._check_salary(job.get('salary', ''))

            # Match if title and location match, and salary meets criteria (if disclosed)
            if title_match and location_match:
                if salary_match or job.get('salary', '') == 'Not specified':
                    job['match_score'] = self._calculate_match_score(job)
                    matching.append(job)

        return matching

    def _check_salary(self, salary_str):
        """Check if salary meets minimum threshold"""
        if not salary_str or salary_str == 'Not specified':
            return True  # Don't filter out if salary not disclosed

        # Extract numbers from salary string
        import re
        numbers = re.findall(r'\d+', salary_str.replace(',', ''))

        if numbers:
            # Get the highest number (usually the max of the range)
            max_salary = max([int(n) for n in numbers])

            # Handle k notation
            if 'k' in salary_str.lower():
                max_salary *= 1000

            return max_salary >= self.criteria['min_salary']

        return True

    def _calculate_match_score(self, job):
        """Calculate how well job matches criteria (0-100)"""
        score = 0

        # Title exact match
        if 'VP of Growth' in job.get('title', ''):
            score += 50
        elif 'VP' in job.get('title', '') and 'Growth' in job.get('title', ''):
            score += 40

        # Location preference
        if 'San Francisco' in job.get('location', '') or 'SF' in job.get('location', ''):
            score += 30
        elif 'New York' in job.get('location', ''):
            score += 25
        elif 'Remote' in job.get('location', ''):
            score += 20

        # Salary disclosed and meets criteria
        if self._check_salary(job.get('salary', '')) and job.get('salary', '') != 'Not specified':
            score += 20

        return min(score, 100)


if __name__ == "__main__":
    # Test
    client = JobsClient()

    print("New Job Matches:")
    jobs = client.get_new_jobs()

    if not jobs:
        print("  No new matches")
    else:
        for job in jobs:
            print(f"\n  • {job.get('title')} at {job.get('company')}")
            print(f"    {job.get('location')} - {job.get('salary')}")
            print(f"    Source: {job.get('source')}")
            print(f"    Match Score: {job.get('match_score', 0)}/100")
