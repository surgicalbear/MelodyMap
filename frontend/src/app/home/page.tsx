'use client'
import { AuthGuard } from "../components/AuthGuard"

export default function Home(){
    return(
      <AuthGuard>
         <div>authed</div>
      </ AuthGuard>
    )
}