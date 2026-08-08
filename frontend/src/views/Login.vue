<template>

<div class="container mt-5">

<div class="row justify-content-center">

<div class="col-md-5">

<div class="card shadow">

<div class="card-body">

<h3 class="text-center mb-4">
Placement Portal Login
</h3>

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
class="btn btn-primary w-100"
@click="login"
>
Login
</button>

<p class="text-danger mt-3">
{{message}}
</p>

<hr>

<div class="text-center">

<router-link to="/student-register">
Student Register
</router-link>

<br><br>

<router-link to="/company-register">
Company Register
</router-link>

</div>

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

const email=ref("")
const password=ref("")
const message=ref("")

function login(){

axios.post("http://127.0.0.1:5000/login",{

email:email.value,
password:password.value

})

.then((res)=>{


localStorage.setItem("token",res.data.token)
localStorage.setItem("role",res.data.role)

if(res.data.role=="admin"){
router.push("/admin")
}

if(res.data.role=="student"){
router.push("/student")
}

if(res.data.role=="company"){
router.push("/company")
}

})

.catch((err)=>{

message.value=err.response.data.message

})

}

</script>