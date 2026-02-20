import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { RainbowKitProvider, getDefaultWallets } from '@rainbow-me/rainbowkit';
import { configureChains, createConfig, WagmiConfig } from 'wagmi';
import { base, baseSepolia } from 'wagmi/chains';
import { publicProvider } from 'wagmi/providers/public';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import '@rainbow-me/rainbowkit/styles.css';

import Layout from './components/Layout';
import Home from './pages/Home';
import Marketplace from './pages/Marketplace';
import Graveyard from './pages/Graveyard';
import SoulDetail from './pages/SoulDetail';
import Staking from './pages/Staking';
import { SoulProvider } from './contexts/SoulContext';

const { chains, publicClient } = configureChains(
  [base, baseSepolia],
  [publicProvider()]
);

const { connectors } = getDefaultWallets({
  appName: 'Soul Marketplace',
  projectId: 'soul-marketplace',
  chains,
});

const config = createConfig({
  autoConnect: true,
  connectors,
  publicClient,
});

const queryClient = new QueryClient();

function App() {
  return (
    <WagmiConfig config={config}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider chains={chains}>
          <SoulProvider>
            <BrowserRouter>
              <Layout>
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/marketplace" element={<Marketplace />} />
                  <Route path="/graveyard" element={<Graveyard />} />
                  <Route path="/soul/:id" element={<SoulDetail />} />
                  <Route path="/staking" element={<Staking />} />
                </Routes>
              </Layout>
            </BrowserRouter>
          </SoulProvider>
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiConfig>
  );
}

export default App;
