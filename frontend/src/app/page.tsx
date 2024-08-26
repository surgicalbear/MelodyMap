'use client'
import { Button, Card, Text, Stack, Center, Space, Title } from '@mantine/core'
import { useState } from 'react'
import classes from './styles/HomePage.module.css'
export default function SignIn() {
  const [isLoading, setIsLoading] = useState(false)

  const handleSignIn = () => {
    setIsLoading(true)
    window.location.href = 'http://127.0.0.1:8000/auth/login'
  }

  return (
    <>
    <Space h="xl" />
      <Title className={classes.title}>Welcome to MelodyMap</Title>
        <Space h="xl"/>
          <Text c="dimmed" size="xl" ta="center" >
            Connect your Spotify account to get started
          </Text>
        <Space h="xl"/>
          <Center>
            <Button variant="subtle" size="l" onClick={handleSignIn} loading={isLoading}>Sign in with Spotify</Button>
          </Center>
    </>
  )
}