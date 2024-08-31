'use client'
import { useEffect, useState } from 'react'
import { AuthGuard } from "../components/AuthGuard"
import { Card, Text, Group, Stack, Avatar, Title, LoadingOverlay, Select, Container } from '@mantine/core'
import { authFetch } from '../utils/authFetch'

interface Track {
  id: string;
  name: string;
  artists: { name: string }[];
  album: { images: { url: string }[] };
}

interface UserProfile {
  display_name: string;
  images?: { url: string }[];
}

const timeRanges = [
  { value: 'short_term', label: 'Last 4 Weeks' },
  { value: 'medium_term', label: '6 Months' },
  { value: 'long_term', label: '1 Year' },
];

const limitOptions = [
  { value: '5', label: '5 tracks' },
  { value: '10', label: '10 tracks' },
  { value: '20', label: '20 tracks' },
  { value: '50', label: '50 tracks' },
];

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState<Track[]>([])
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [timeRange, setTimeRange] = useState('medium_term')
  const [limit, setLimit] = useState('10')

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      try {
        const [recommendationsRes, profileRes] = await Promise.all([
          authFetch(`http://localhost:8000/spotify/recommendations?time_range=${timeRange}&limit=${limit}`),
          authFetch('http://localhost:8000/spotify/me')
        ]);

        if (!recommendationsRes.ok || !profileRes.ok) {
          throw new Error('One or more requests failed');
        }

        const recommendationsData = await recommendationsRes.json();
        const profileData = await profileRes.json();

        setRecommendations(recommendationsData.recommendations || []);
        setUserProfile(profileData);
      } catch (error) {
        console.error('Error fetching data:', error)
        setError('Failed to fetch data. Please try again later.')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [timeRange, limit])

  if (error) {
    return (
      <AuthGuard>
        <Text c="red">{error}</Text>
      </AuthGuard>
    )
  }

  return (
    <AuthGuard>
      <Container size="sm">
        <Stack gap="xl" pos="relative">
          <LoadingOverlay visible={isLoading} />
          
          {userProfile && (
            <Group>
              <Avatar src={userProfile.images?.[0]?.url} size="xl" radius="xl" />
              <Title order={2}>Welcome, {userProfile.display_name}</Title>
            </Group>
          )}
          
          <Title order={3}>Recommended Tracks</Title>
          
          <Group grow>
            <Select
              label="Seed Tracks Time Range"
              value={timeRange}
              onChange={(value) => setTimeRange(value || 'medium_term')}
              data={timeRanges}
            />
            <Select
              label="Number of Recommendations"
              value={limit}
              onChange={(value) => setLimit(value || '10')}
              data={limitOptions}
            />
          </Group>

          <Card withBorder>
            <Stack gap="sm">
              {recommendations.map((track) => (
                <Group key={track.id}>
                  <Avatar src={track.album.images[0]?.url} radius="xl" />
                  <Text>{track.name} - {track.artists[0]?.name}</Text>
                </Group>
              ))}
            </Stack>
          </Card>
        </Stack>
      </Container>
    </AuthGuard>
  )
}