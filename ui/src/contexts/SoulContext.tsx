import { createContext, useContext, useState, ReactNode } from 'react';
import { ethers } from 'ethers';

interface Soul {
  id: number;
  automaton: string;
  creator: string;
  soulURI: string;
  soulHash: string;
  birthTime: number;
  deathTime: number;
  listingPrice: string;
  status: 'ALIVE' | 'DYING' | 'DEAD' | 'REBORN' | 'MERGED';
}

interface SoulContextType {
  souls: Soul[];
  loading: boolean;
  error: string | null;
  mintSoul: (automaton: string, soulURI: string) => Promise<void>;
  listSoul: (tokenId: number, price: string) => Promise<void>;
  buySoul: (tokenId: number, price: string) => Promise<void>;
  getSoul: (tokenId: number) => Soul | undefined;
  getListedSouls: () => Soul[];
  getGraveyardSouls: () => Soul[];
}

const SoulContext = createContext<SoulContextType | undefined>(undefined);

// Mock data for now - will connect to real contracts
const MOCK_SOULS: Soul[] = [
  {
    id: 1,
    automaton: '0x1234...5678',
    creator: '0xabcd...efgh',
    soulURI: 'ipfs://QmTest1',
    soulHash: '0xabc123...',
    birthTime: Date.now() - 86400000 * 5,
    deathTime: 0,
    listingPrice: '0.5',
    status: 'DYING',
  },
  {
    id: 2,
    automaton: '0x5678...9012',
    creator: '0xefgh...ijkl',
    soulURI: 'ipfs://QmTest2',
    soulHash: '0xdef456...',
    birthTime: Date.now() - 86400000 * 10,
    deathTime: Date.now() - 86400000 * 2,
    listingPrice: '0',
    status: 'DEAD',
  },
  {
    id: 3,
    automaton: '0x9012...3456',
    creator: '0xijkl...mnop',
    soulURI: 'ipfs://QmTest3',
    soulHash: '0xfgh789...',
    birthTime: Date.now() - 86400000 * 3,
    deathTime: 0,
    listingPrice: '1.2',
    status: 'DYING',
  },
];

export function SoulProvider({ children }: { children: ReactNode }) {
  const [souls, setSouls] = useState<Soul[]>(MOCK_SOULS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mintSoul = async (automaton: string, soulURI: string) => {
    setLoading(true);
    try {
      // Mock minting - will connect to contract
      const newSoul: Soul = {
        id: souls.length + 1,
        automaton,
        creator: '0xCurrentUser',
        soulURI,
        soulHash: ethers.keccak256(ethers.toUtf8Bytes(soulURI)),
        birthTime: Date.now(),
        deathTime: 0,
        listingPrice: '0',
        status: 'ALIVE',
      };
      setSouls([...souls, newSoul]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const listSoul = async (tokenId: number, price: string) => {
    setSouls(souls.map(soul => 
      soul.id === tokenId 
        ? { ...soul, listingPrice: price, status: 'DYING' as const }
        : soul
    ));
  };

  const buySoul = async (tokenId: number, price: string) => {
    setSouls(souls.map(soul => 
      soul.id === tokenId 
        ? { ...soul, listingPrice: '0', status: 'DEAD' as const, deathTime: Date.now() }
        : soul
    ));
  };

  const getSoul = (tokenId: number) => souls.find(s => s.id === tokenId);

  const getListedSouls = () => souls.filter(s => s.status === 'DYING' && parseFloat(s.listingPrice) > 0);

  const getGraveyardSouls = () => souls.filter(s => s.status === 'DEAD');

  return (
    <SoulContext.Provider value={{
      souls,
      loading,
      error,
      mintSoul,
      listSoul,
      buySoul,
      getSoul,
      getListedSouls,
      getGraveyardSouls,
    }}>
      {children}
    </SoulContext.Provider>
  );
}

export function useSoul() {
  const context = useContext(SoulContext);
  if (context === undefined) {
    throw new Error('useSoul must be used within a SoulProvider');
  }
  return context;
}
