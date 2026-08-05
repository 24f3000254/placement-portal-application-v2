<template>

<div class="container mt-5">

<div class="row justify-content-center">

<div class="col-md-6">

<div class="card shadow">

<div class="card-body">

<h3 class="text-center mb-4">Company Registration</h3>

<input class="form-control mb-2" placeholder="Company Name" v-model="company_name">

<input class="form-control mb-2" placeholder="Email" v-model="email">

<input type="password" class="form-control mb-2" placeholder="Password" v-model="password">

<input class="form-control mb-2" placeholder="Industry" v-model="industry">

<input class="form-control mb-2" placeholder="Location" v-model="location">

<input class="form-control mb-2" placeholder="Website" v-model="website">

<input class="form-control mb-3" placeholder="HR Contact" v-model="hr_contact">

<button class="btn btn-success w-100" @click="registerCompany">
Register
</button>

<p class="text-danger mt-3">{{message}}</p>

<router-link to="/login">
Back to Login
</router-link>

</div>

</div>

</div>

</div>

</div>

</template>

<script setup>

import {ref} from "vue"
import axios from "axios"
import {useRouter} from "vue-router"

const router=useRouter()

const company_name=ref("")
const email=ref("")
const password=ref("")
const industry=ref("")
const location=ref("")
const website=ref("")
const hr_contact=ref("")
const message=ref("")

function registerCompany(){

axios.post("http://127.0.0.1:5000/company/register",{

company_name:company_name.value,
email:email.value,
password:password.value,
industry:industry.value,
location:location.value,
website:website.value,
hr_contact:hr_contact.value

})

.then(()=>{

alert("Company Registered Successfully")

router.push("/login")

})

.catch((err)=>{

message.value=err.response.data.message

})

}

</script>