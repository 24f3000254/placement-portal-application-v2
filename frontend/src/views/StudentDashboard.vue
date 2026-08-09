<template>

<div class="container mt-4">

<h2>Student Dashboard</h2>

<button
class="btn btn-danger float-end"
@click="logout">
Logout
</button>

<br><br>

<h4>My Profile</h4>

<div class="card p-3 mb-4">

<input
class="form-control mb-2"
v-model="profile.name"
placeholder="Name">

<input
class="form-control mb-2"
v-model="profile.email"
disabled>

<input
class="form-control mb-2"
v-model="profile.education"
placeholder="Education">

<input
class="form-control mb-2"
v-model="profile.branch"
placeholder="Branch">

<input
class="form-control mb-2"
v-model="profile.year"
placeholder="Year">

<input
class="form-control mb-2"
v-model="profile.cgpa"
placeholder="CGPA">

<input
class="form-control mb-2"
v-model="profile.skills"
placeholder="Skills">

<textarea
class="form-control mb-2"
v-model="profile.experience"
placeholder="Experience">
</textarea>

<button
class="btn btn-primary me-2"
@click="updateProfile">
Update Profile
</button>

<input
type="file"
class="form-control mt-3"
accept="application/pdf,.pdf"
@change="selectResume">

<button
class="btn btn-success mt-2"
@click="uploadResume">
Upload Resume
</button>

<p v-if="profile.resume" class="mt-2">
Current Resume: {{ profile.resume }}
</p>

</div>


<h4>Available Jobs</h4>

<input
class="form-control mb-3"
v-model="search"
@input="loadJobs"
placeholder="Search company, job or skill">

<table class="table table-bordered">

<thead>

<tr>

<th>Company</th>
<th>Title</th>
<th>Salary</th>
<th>Experience</th>
<th>Skills</th>
<th>Deadline</th>
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

<td>{{ job.skills_required }}</td>

<td>{{ job.deadline }}</td>

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

{{ job.application_status }}

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


<hr>

<h4>Placement History</h4>

<table class="table table-bordered">

<thead>

<tr>

<th>Company</th>
<th>Job</th>
<th>Salary</th>
<th>Joining Date</th>
<th>Status</th>
<th>Download</th>

</tr>

</thead>

<tbody>

<tr
v-for="placement in placements"
:key="placement.id">

<td>{{ placement.company }}</td>
<td>{{ placement.job }}</td>
<td>{{ placement.salary }}</td>
<td>{{ placement.joining_date }}</td>

<td>
<span class="badge bg-success">
{{ placement.status }}
</span>
</td>

<td>

<button
class="btn btn-primary btn-sm"
@click="downloadPlacement(placement.id)">
Download
</button>

</td>

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
const placements=ref([])

const search=ref("")

const profile=ref({
name:"",
email:"",
education:"",
branch:"",
year:"",
cgpa:"",
skills:"",
experience:"",
resume:""
})

const resumeFile=ref(null)


function loadProfile(){

axios.get(
"http://127.0.0.1:5000/student/profile",
{
headers:{
Authorization:"Bearer "+localStorage.getItem("token")
}})

.then(res=>{
profile.value=res.data
})

}


function updateProfile(){

axios.put(
"http://127.0.0.1:5000/student/profile",
profile.value,
{
headers:{
Authorization:"Bearer "+localStorage.getItem("token")
}})

.then(res=>{
alert(res.data.message)
loadProfile()
})

}


function selectResume(event){

    console.log("FILE EVENT:", event)
    console.log("FILES:", event.target.files)

    if(event.target.files.length > 0){

        resumeFile.value = event.target.files[0]

        console.log("SELECTED:", resumeFile.value.name)

    }
}


function uploadResume(){

    if(!resumeFile.value){
        alert("Select a PDF resume")
        return
    }

    let formData = new FormData()

    formData.append("resume", resumeFile.value)

    console.log("FILE:", resumeFile.value)
    console.log("FORM DATA:", formData.get("resume"))

    axios.post(
        "http://127.0.0.1:5000/student/resume",
        formData,
        {
            headers:{
                Authorization:"Bearer "+localStorage.getItem("token")
            }
        }
    )
    .then(res=>{

        console.log("UPLOAD SUCCESS:", res.data)

        alert(res.data.message)

        loadProfile()

    })
    .catch(err=>{

        console.log("UPLOAD ERROR:", err)

        if(err.response){
            console.log("STATUS:", err.response.status)
            console.log("SERVER:", err.response.data)
            alert(err.response.data.message)
        }
    })
}


function loadJobs(){

axios.get(
"http://127.0.0.1:5000/student/jobs",
{
params:{
search:search.value
},
headers:{
Authorization:"Bearer "+localStorage.getItem("token")
}})

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
}})

.then(res=>{
applications.value=res.data
})

}


function loadPlacements(){

axios.get(
"http://127.0.0.1:5000/student/placements",
{
headers:{
Authorization:"Bearer "+localStorage.getItem("token")
}})

.then(res=>{
placements.value=res.data
})

}


function applyJob(id){

axios.post(
"http://127.0.0.1:5000/student/apply/"+id,
{},
{
headers:{
Authorization:"Bearer "+localStorage.getItem("token")
}})

.then(res=>{

alert(res.data.message)

loadJobs()
loadApplications()

})

.catch(err=>{

if(err.response){
alert(err.response.data.message)
}

})

}


function downloadPlacement(id){

axios.get(
"http://127.0.0.1:5000/student/placement/"+id+"/download",
{
responseType:"blob",
headers:{
Authorization:"Bearer "+localStorage.getItem("token")
}})

.then(res=>{

let url=window.URL.createObjectURL(
new Blob([res.data])
)

let link=document.createElement("a")

link.href=url

link.setAttribute(
"download",
"placement_confirmation.txt"
)

document.body.appendChild(link)

link.click()

link.remove()

})

}


function logout(){

localStorage.clear()

router.push("/login")

}


onMounted(()=>{

loadProfile()
loadJobs()
loadApplications()
loadPlacements()

})

</script>