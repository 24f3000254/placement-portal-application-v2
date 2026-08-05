<template>

<div class="container mt-5">

<div class="row justify-content-center">

<div class="col-md-6">

<div class="card shadow">

<div class="card-body">

<h3 class="text-center mb-4">
Student Registration
</h3>

<div class="mb-3">

<label>Name</label>

<input
class="form-control"
v-model="name"
>

</div>

<div class="mb-3">

<label>Email</label>

<input
type="email"
class="form-control"
v-model="email"
>

</div>

<div class="mb-3">

<label>Password</label>

<input
type="password"
class="form-control"
v-model="password"
>

</div>

<button
class="btn btn-success w-100"
@click="registerStudent"
>

Register

</button>

<p class="text-danger mt-3">

{{message}}

</p>

<br>

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

const name=ref("")

const email=ref("")

const password=ref("")

const message=ref("")

function registerStudent(){

axios.post("http://127.0.0.1:5000/student/register",{

name:name.value,

email:email.value,

password:password.value

})

.then(()=>{

alert("Registration Successful")

router.push("/login")

})

.catch((err)=>{

message.value=err.response.data.message

})

}

</script>