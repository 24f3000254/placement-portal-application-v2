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
class="btn btn-success btn-sm"
@click="approve(company.user_id)"
>
Approve
</button>

</td>

</tr>

</tbody>

</table>

</div>

</template>

<script setup>

import {ref,onMounted} from "vue"
import axios from "axios"

const companies = ref([])

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

        console.log(res.data)

        companies.value = res.data

    })

    .catch((err)=>{

        console.log(err.response)

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

onMounted(()=>{
loadDashboard()
loadCompanies()
})

</script>