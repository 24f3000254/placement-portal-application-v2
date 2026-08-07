<template>

<div class="container mt-4">

<h2>Student Dashboard</h2>

<button
class="btn btn-danger float-end"
@click="logout">

Logout

</button>

<br><br>

<h4>Available Jobs</h4>

<table class="table table-bordered">

<thead>

<tr>

<th>Company</th>

<th>Title</th>

<th>Salary</th>

<th>Experience</th>

<th>Status</th>

<th>Action</th>

</tr>

</thead>

<tbody>

<tr
v-for="job in jobs"
:key="job.id">

<td>{{ job.company }}</td>

<td>{{ job.title }}</td>

<td>{{ job.salary }}</td>

<td>{{ job.experience }}</td>

<td>{{ job.status }}</td>

<td>

<button
v-if="!job.applied"
class="btn btn-success btn-sm"
@click="applyJob(job.id)">

Apply

</button>

<span
v-else
class="badge bg-primary">

Applied

</span>

</td>

</tr>

</tbody>

</table>

<hr>

<h4>My Applications</h4>

<table class="table table-bordered">

<thead>

<tr>

<th>Company</th>

<th>Job</th>

<th>Status</th>

<th>Applied On</th>

<th>Interview</th>

</tr>

</thead>

<tbody>

<tr
v-for="app in applications"
:key="app.id">

<td>{{ app.company }}</td>

<td>{{ app.job }}</td>

<td>{{ app.status }}</td>

<td>{{ app.application_date }}</td>

<td>{{ app.interview_date }}</td>

</tr>

</tbody>

</table>

</div>

</template>

<script setup>

import axios from "axios"

import {ref,onMounted} from "vue"

import {useRouter} from "vue-router"

const router=useRouter()

const jobs=ref([])

const applications=ref([])

function loadJobs(){

axios.get(

"http://127.0.0.1:5000/student/jobs",

{

headers:{

Authorization:"Bearer "+localStorage.getItem("token")

}

}

)

.then(res=>{

jobs.value=res.data

})

}

function loadApplications(){

axios.get(

"http://127.0.0.1:5000/student/applications",

{

headers:{

Authorization:"Bearer "+localStorage.getItem("token")

}

}

)

.then(res=>{

applications.value=res.data

})

}

function applyJob(id){

axios.post(

"http://127.0.0.1:5000/student/apply/"+id,

{},

{

headers:{

Authorization:"Bearer "+localStorage.getItem("token")

}

}

)

.then(()=>{

alert("Application Submitted")

loadJobs()

loadApplications()

})

}

function logout(){

axios.post(

"http://127.0.0.1:5000/logout",

{},

{

headers:{

Authorization:"Bearer "+localStorage.getItem("token")

}

}

)

.then(()=>{

localStorage.clear()

router.push("/login")

})

}

onMounted(()=>{

loadJobs()

loadApplications()

})

</script>