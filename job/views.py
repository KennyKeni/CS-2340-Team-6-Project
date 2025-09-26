from django.shortcuts import render
from recruiter.models import JobPosting
from django.db.models import Q

def search_jobs(request):
	jobs = JobPosting.objects.all()
	title = request.GET.get('title', '').strip()
	skills = request.GET.get('skills', '').strip()
	location = request.GET.get('location', '').strip()
	salary_min = request.GET.get('salary_min', '').strip()
	salary_max = request.GET.get('salary_max', '').strip()
	remote = request.GET.get('remote', '')
	visa = request.GET.get('visa', '')

	if title:
		jobs = jobs.filter(title__icontains=title)
	if skills:
		for skill in [s.strip() for s in skills.split(',') if s.strip()]:
			jobs = jobs.filter(skills_required__icontains=skill)
	if location:
		jobs = jobs.filter(location__icontains=location)
	if salary_min:
		jobs = jobs.filter(salary__regex=r'\d+')  # crude filter, assumes salary is a string
	if salary_max:
		jobs = jobs.filter(salary__regex=r'\d+')
	if remote == 'remote':
		jobs = jobs.filter(remote=True)
	elif remote == 'onsite':
		jobs = jobs.filter(remote=False)
	if visa == 'yes':
		jobs = jobs.filter(visa_sponsorship=True)
	elif visa == 'no':
		jobs = jobs.filter(visa_sponsorship=False)

	context = {
		'jobs': jobs,
	}
	return render(request, 'job/search.html', context)