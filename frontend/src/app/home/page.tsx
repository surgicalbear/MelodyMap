'use client'
import { useEffect, useState } from 'react'
import { AuthGuard } from "../components/AuthGuard"
import { Card, Text, Group, Stack, Avatar, Title, LoadingOverlay, Button, Select, Container } from '@mantine/core'
import { authFetch } from '../utils/authFetch'
import Link from 'next/link'

interface Artist {
  name: string;
  images: { url: string }[];
}

interface Track {
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

export default function Home() {
  const [topArtists, setTopArtists] = useState<Artist[]>([])
  const [topTracks, setTopTracks] = useState<Track[]>([])
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [timeRange, setTimeRange] = useState('medium_term')

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      try {
        const [artistsRes, tracksRes, profileRes] = await Promise.all([
          authFetch(`http://localhost:8000/spotify/top/artists?time_range=${timeRange}&limit=15`),
          authFetch(`http://localhost:8000/spotify/top/tracks?time_range=${timeRange}&limit=15`),
          authFetch('http://localhost:8000/spotify/me')
        ]);

        if (!artistsRes.ok || !tracksRes.ok || !profileRes.ok) {
          throw new Error('One or more requests failed');
        }

        const artistsData = await artistsRes.json();
        const tracksData = await tracksRes.json();
        const profileData = await profileRes.json();

        setTopArtists(artistsData.items || []);
        setTopTracks(tracksData.items || []);
        setUserProfile(profileData);
      } catch (error) {
        console.error('Error fetching data:', error);
        setError('Failed to fetch data. Please try again later.');
      } finally {
        setIsLoading(false)
      }
    };

    fetchData();
  }, [timeRange]);

  if (error) {
    return (
      <AuthGuard>
        <Text c="red">{error}</Text>
      </AuthGuard>
    );
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

          <Select
            label="Select Time Range"
            value={timeRange}
            onChange={(value) => setTimeRange(value || 'medium_term')}
            data={timeRanges}
          />

          <Card withBorder>
            <Title order={3} mb="md">Your Top Artists</Title>
            <Stack gap="sm">
              {topArtists.map((artist, index) => (
                <Group key={index}>
                  <Avatar src={artist.images[0]?.url} radius="xl" />
                  <Text>{artist.name}</Text>
                </Group>
              ))}
            </Stack>
          </Card>

          <Card withBorder>
            <Title order={3} mb="md">Your Top Tracks</Title>
            <Stack gap="sm">
              {topTracks.map((track, index) => (
                <Group key={index}>
                  <Avatar src={track.album.images[0]?.url} radius="xl" />
                  <Text>{track.name} - {track.artists[0]?.name}</Text>
                </Group>
              ))}
            </Stack>
          </Card>

          <Link href="/recommendations" passHref>
            <Button component="a">View Recommendations</Button>
          </Link>
        </Stack>
      </Container>
    </AuthGuard>
  )
}
