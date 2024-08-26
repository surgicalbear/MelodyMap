'use client'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Text, Center, Container, Title } from '@mantine/core'

export default function Callback() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const handleCallback = () => {
      const urlParams = new URLSearchParams(window.location.search)
      const access_token = urlParams.get('access_token')

      if (access_token) {
        localStorage.setItem('access_token', access_token)
        router.push('/home') 
      } else {
        console.error('No access token received')
        setError('Authentication failed. Please try again.')
      }
    }

    handleCallback()
  }, [router])

  if (error) {
    return (
      <Container>
        <Title order={2} c="red">Error</Title>
        <Text>{error}</Text>
      </Container>
    )
  }

  return (
    <Center style={{ height: '100vh' }}>
      <Text>Processing your sign in...</Text>
    </Center>
  )
}
