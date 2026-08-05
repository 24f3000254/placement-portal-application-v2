<template>

<div class="container mt-5">

<h2 class="mb-4">Admin Dashboard</h2>

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

const companies=ref([])

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

companies.value=res.data

})

}

function approve(id){

axios.put(

"http://127.0.0.1:5000/admin/approve-company/"+id,

{},

{

headers:{

Authorization:"Bearer "+localStorage.getItem("token")

}

}

)

.then(()=>{

alert("Company Approved")

loadCompanies()

})

}

onMounted(()=>{

loadCompanies()

})

</script>