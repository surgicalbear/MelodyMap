'use client'
import { AppShell, Burger, Group, Button, UnstyledButton, ThemeIcon} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import { IconLogin2, IconLogout2, IconTimeline } from '@tabler/icons-react';
import Link from 'next/link'

export function AppShellLayout({ children }: { children: React.ReactNode }) {
  const [mobileOpened, { toggle: toggleMobile }] = useDisclosure();
  const [desktopOpened, { toggle: toggleDesktop }] = useDisclosure();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('access_token');
      setIsAuthenticated(!!token);
    };
    checkAuth();
  }, [pathname]);

  const handleSignOut = () => {
    localStorage.removeItem('access_token');
    setIsAuthenticated(false);
    router.push('/');
  };

  const handleSignIn = () => {
    router.push('http://127.0.0.1:8000/auth/login');
  };
  const renderAuthButton = () => {
    if (pathname === '/') {
      return <Button onClick={handleSignIn}>Sign In</Button>;
    } else if (pathname === '/home' && isAuthenticated) {
      return <Button onClick={handleSignOut}>Sign Out</Button>;
    }
    return null;
  };

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: 'sm',
        collapsed: { mobile: !mobileOpened, desktop: !desktopOpened },
      }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group>
            <Burger opened={mobileOpened} onClick={toggleMobile} hiddenFrom="sm" size="sm" />
            <Burger opened={desktopOpened} onClick={toggleDesktop} visibleFrom="sm" size="sm" />
          </Group>
          {renderAuthButton()}
        </Group>
      </AppShell.Header>
      <AppShell.Navbar p="md">
        {(isAuthenticated ? (
          <>
            <UnstyledButton onClick={handleSignOut} mt="sm">
              <Group>
                <ThemeIcon color="red" variant="light">
                  <IconLogout2 size="1rem" />
                </ThemeIcon>
                Sign Out
              </Group>
            </UnstyledButton>
            <Link href="/recommendations" passHref>
            <UnstyledButton component="a" mt="sm">
              <Group>
                <ThemeIcon color="cyan" variant="light">
                  <IconTimeline size="1rem" />
                </ThemeIcon>
                Recommendations
              </Group>
            </UnstyledButton>
          </Link>
          </>
          ) : (
            <UnstyledButton onClick={handleSignIn} mt="sm">
              <Group>
                <ThemeIcon color="cyan" variant="light">
                  <IconLogin2 size="1rem" />
                </ThemeIcon>
                Sign In
              </Group>
            </UnstyledButton>
          )
        )}
      </AppShell.Navbar>
      <AppShell.Main>
          {children}
      </AppShell.Main>
    </AppShell>
  );
}
