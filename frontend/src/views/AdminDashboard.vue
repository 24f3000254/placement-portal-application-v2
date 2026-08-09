<template>

<div class="container mt-5">

<h2 class="mb-4">Admin Dashboard</h2>

<div class="row mb-4">

<div class="col-md-3">
<div class="card text-center">
<div class="card-body">
<h5>Students</h5>
<h3>{{dashboard.students}}</h3>
</div>
</div>
</div>

<div class="col-md-3">
<div class="card text-center">
<div class="card-body">
<h5>Companies</h5>
<h3>{{dashboard.companies}}</h3>
</div>
</div>
</div>

<div class="col-md-3">
<div class="card text-center">
<div class="card-body">
<h5>Jobs</h5>
<h3>{{dashboard.jobs}}</h3>
</div>
</div>
</div>

<div class="col-md-3">
<div class="card text-center">
<div class="card-body">
<h5>Applications</h5>
<h3>{{dashboard.applications}}</h3>
</div>
</div>
</div>

</div>

<h4>Registered Companies</h4>
<table class="table table-bordered">
<thead>
<tr>
<th>Company</th>
<th>Industry</th>
<th>Location</th>
<th>Status</th>
<th>Action</th>
</tr>
</thead>

<tbody>
<tr v-for="company in companies" :key="company.id">
<td>{{company.company_name}}</td>
<td>{{company.industry}}</td>
<td>{{company.location}}</td>
<td>
<span v-if="company.approved">
Approved
</span>
<span v-else>
Pending
</span>
</td>

<td>
<button
v-if="!company.approved"
class="btn btn-success btn-sm me-1"
@click="approve(company.user_id)">Approve</button>

<button
v-if="company.approved"
class="btn btn-danger btn-sm"
@click="rejectCompany(company.user_id)">Reject</button>
</td>
</tr>
</tbody>
</table>


<hr>

<h4>Students</h4>
<table class="table table-bordered">
<thead>
<tr>
<th>Name</th>
<th>Email</th>
<th>Education</th>
<th>Branch</th>
<th>Year</th>
<th>CGPA</th>
</tr>
</thead>

<tbody>
<tr
v-for="student in students"
:key="student.id">
<td>{{student.name}}</td>
<td>{{student.email}}</td>
<td>{{student.education}}</td>
<td>{{student.branch}}</td>
<td>{{student.year}}</td>
<td>{{student.cgpa}}</td>
</tr>
</tbody>
</table>

<hr>

<h4>Jobs</h4>
<table class="table table-bordered">
<thead>
<tr>
<th>Company</th>
<th>Job</th>
<th>Experience</th>
<th>Salary</th>
<th>Status</th>
</tr>
</thead>

<tbody>
<tr
v-for="job in jobs"
:key="job.id">
<td>{{job.company}}</td>
<td>{{job.title}}</td>
<td>{{job.experience}}</td>
<td>{{job.salary}}</td>
<td>

{{job.status}}

<br>
<button
v-if="job.status == 'Pending'"
class="btn btn-success btn-sm me-1 mt-1"
@click="approveJob(job.id)">Approve</button>

<button
v-if="job.status == 'Pending'"
class="btn btn-danger btn-sm mt-1"
@click="rejectJob(job.id)">Reject</button>

</td>
</tr>
</tbody>
</table>

<hr>

<h4>Applications</h4>
<table class="table table-bordered">
<thead>
<tr>
<th>Student</th>
<th>Company</th>
<th>Job</th>
<th>Status</th>
</tr>
</thead>

<tbody>
<tr
v-for="application in applications"
:key="application.id">
<td>{{application.student}}</td>
<td>{{application.company}}</td>
<td>{{application.job}}</td>
<td>{{application.status}}</td>
</tr>
</tbody>
</table>


<hr>
<h4>Placements</h4>
<table class="table table-bordered">
<thead>
<tr>
<th>Student</th>
<th>Email</th>
<th>Company</th>
<th>Job</th>
<th>Salary</th>
<th>Joining Date</th>
</tr>
</thead>
<tbody>

<tr
v-for="placement in placements"
:key="placement.id">
<td>{{ placement.student }}</td>
<td>{{ placement.email }}</td>
<td>{{ placement.company }}</td>
<td>{{ placement.job }}</td>
<td>{{ placement.salary }}</td>
<td>{{ placement.joining_date }}</td>
</tr>
</tbody>
</table>

</div>
</template>

<script setup>

import {ref,onMounted} from "vue"
import axios from "axios"

const companies = ref([])
const students = ref([])
const jobs = ref([])
const applications = ref([])
const placements = ref([])

const dashboard = ref({
students:0,
companies:0,
jobs:0,
applications:0
})

function loadDashboard(){
axios.get(
"http://127.0.0.1:5000/admin/dashboard",
{
headers:{
Authorization:"Bearer "+localStorage.getItem("token")
}})
 

.then((res)=>{
dashboard.value = res.data
})
}

function loadCompanies(){
    axios.get(
        "http://127.0.0.1:5000/admin/companies",
        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }
        }
    )

    .then((res)=>{
        
        companies.value = res.data
    })

    .catch((err)=>{

    })
}


function loadStudents(){

    axios.get(
        "http://127.0.0.1:5000/admin/students",
        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }
        }
    )

    .then((res)=>{
        students.value = res.data
    })

}

function loadJobs(){

    axios.get(
        "http://127.0.0.1:5000/admin/jobs",
        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }
        }
    )

    .then((res)=>{
        jobs.value = res.data
    })

}

function loadApplications(){
    axios.get(
        "http://127.0.0.1:5000/admin/applications",
        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }
        }
    )
    .then((res)=>{
        applications.value = res.data
    })

}

function loadPlacements(){
    axios.get(
        "http://127.0.0.1:5000/admin/placements",
        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }
        }
    )

    .then((res)=>{
        placements.value = res.data
    })
}

function approveJob(id){
axios.put(
"http://127.0.0.1:5000/admin/approve-job/"+id,
{},
{
headers:{
Authorization:"Bearer "+localStorage.getItem("token")
}})

.then(res=>{

alert(res.data.message)

loadJobs()

})

.catch(err=>{

if(err.response){
alert(err.response.data.message)
}

})

}


function rejectJob(id){
axios.put(
"http://127.0.0.1:5000/admin/reject-job/"+id,
{},
{
headers:{
Authorization:"Bearer "+localStorage.getItem("token")
}})

.then(res=>{

alert(res.data.message)

loadJobs()

})

.catch(err=>{

if(err.response){
alert(err.response.data.message)
}

})

}

function approve(id){
axios.put(
"http://127.0.0.1:5000/admin/approve-company/"+id,
{},

{
headers:{
Authorization:"Bearer "+localStorage.getItem("token")
}}
)

.then(()=>{
alert("Company Approved")
loadCompanies()
})
}

function rejectCompany(id){
    axios.put(
        "http://127.0.0.1:5000/admin/reject-company/"+id,
        {},
        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }
        }
    )

    .then((res)=>{
        alert(res.data.message)
        loadCompanies()
    })

    .catch((err)=>{
        console.log(err)
        if(err.response){
            alert(err.response.data.message)
        }
        else{
            alert("Something went wrong")
        }
    })
}

onMounted(()=>{
loadDashboard()
loadCompanies()
loadStudents()
loadJobs()
loadApplications()
loadPlacements()
})

</script>