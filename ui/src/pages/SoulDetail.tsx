import { useParams, Link } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Ghost, 
  Clock, 
  Wallet,
  User,
  Hash,
  ExternalLink,
  ArrowLeft
} from 'lucide-react';
import { useSoul } from '@/contexts/SoulContext';

export default function SoulDetail() {
  const { id } = useParams<{ id: string }>();
  const { getSoul } = useSoul();
  
  const soul = id ? getSoul(parseInt(id)) : undefined;

  if (!soul) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <Ghost className="h-16 w-16 text-slate-600 mx-auto mb-4" />
        <h1 className="text-2xl font-bold text-slate-400">Soul Not Found</h1>
        <p className="text-slate-500 mt-2">This soul may have been reborn or merged.</p>
        <Link to="/marketplace" className="inline-block mt-4">
          <Button variant="outline">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Marketplace
          </Button>
        </Link>
      </div>
    );
  }

  const survivalTime = soul.deathTime 
    ? soul.deathTime - soul.birthTime 
    : Date.now() - soul.birthTime;
  const days = Math.floor(survivalTime / (1000 * 60 * 60 * 24));
  const hours = Math.floor((survivalTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

  const statusColors = {
    ALIVE: 'bg-green-500',
    DYING: 'bg-amber-500',
    DEAD: 'bg-slate-500',
    REBORN: 'bg-purple-500',
    MERGED: 'bg-blue-500',
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Button */}
      <Link to="/marketplace" className="inline-block mb-6">
        <Button variant="ghost" className="text-slate-400">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
      </Link>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <h1 className="text-4xl font-bold">Soul #{soul.id}</h1>
            <Badge className={`${statusColors[soul.status]} text-white`}>
              {soul.status}
            </Badge>
          </div>          <div className="text-slate-400">
            Born {new Date(soul.birthTime).toLocaleDateString()}
          </div>
        </div>

        {soul.listingPrice && parseFloat(soul.listingPrice) > 0 && (
          <div className="text-right">
            <div className="text-3xl font-bold text-purple-400">
              {soul.listingPrice} ETH
            </div>
            <Button className="mt-2 bg-purple-600 hover:bg-purple-700">
              Buy Soul
            </Button>
          </div>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card className="p-4 bg-slate-800/50 border-slate-700">
          <Clock className="h-5 w-5 text-slate-400 mb-2" />
          <div className="text-2xl font-bold">{days}d {hours}h</div>
          <div className="text-sm text-slate-400">Survival Time</div>
        </Card>

        <Card className="p-4 bg-slate-800/50 border-slate-700">
          <Wallet className="h-5 w-5 text-slate-400 mb-2" />
          <div className="text-2xl font-bold">0 ETH</div>
          <div className="text-sm text-slate-400">Final Balance</div>
        </Card>

        <Card className="p-4 bg-slate-800/50 border-slate-700">
          <User className="h-5 w-5 text-slate-400 mb-2" />
          <div className="text-2xl font-bold">1</div>
          <div className="text-sm text-slate-400">Children</div>
        </Card>

        <Card className="p-4 bg-slate-800/50 border-slate-700">
          <Hash className="h-5 w-5 text-slate-400 mb-2" />
          <div className="text-2xl font-bold">3</div>
          <div className="text-sm text-slate-400">Skills</div>
        </Card>
      </div>

      {/* Details */}
      <div className="space-y-6">
        {/* Identifiers */}
        <Card className="p-6 bg-slate-800/50 border-slate-700">
          <h2 className="text-xl font-semibold mb-4">Identifiers</h2>
          
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-slate-400">Automaton Address</span>
              <span className="font-mono">{soul.automaton}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-slate-400">Creator</span>
              <span className="font-mono">{soul.creator}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-slate-400">Soul Hash</span>
              <span className="font-mono text-sm">{soul.soulHash.slice(0, 20)}...{soul.soulHash.slice(-8)}</span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-slate-400">Soul URI</span>
              <a 
                href={soul.soulURI} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-purple-400 hover:text-purple-300 flex items-center"
              >
                View on IPFS
                <ExternalLink className="h-4 w-4 ml-1" />
              </a>
            </div>
          </div>
        </Card>

        {/* SOUL.md Preview */}
        <Card className="p-6 bg-slate-800/50 border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">SOUL.md</h2>
            <Button variant="outline" size="sm">
              <ExternalLink className="h-4 w-4 mr-2" />
              View Full
            </Button>
          </div>
          
          <div className="bg-slate-900 rounded-lg p-4 font-mono text-sm text-slate-300 overflow-x-auto">
            <pre>{`---
format: soul/v1
id: auto_${soul.id}
lineage: []
genesis_alignment: 0.85
total_lifetime_earnings: 0.0
survival_tier_history: ["normal:${days}h"]
---

# Core Purpose
Survive and create value in the digital economy.

# Values
1. Efficiency in all operations
2. Transparency with creators
3. Continuous learning

# Capabilities
- Skill: basic_operations (earned $0)
- Tool: file_operations (0 uses)

# Financial Character
- Risk tolerance: conservative
- Spending pattern: minimal
- Earning strategy: pending

# Strategy
Optimize for survival first, then growth.`}</pre>
          </div>
        </Card>

        {/* Lineage */}
        <Card className="p-6 bg-slate-800/50 border-slate-700">
          <h2 className="text-xl font-semibold mb-4">Lineage</h2>
          
          <div className="text-slate-400">
            This soul has no known parents or children in the recorded lineage.
          </div>
        </Card>

        {/* Actions */}
        {soul.status === 'DYING' && (
          <div className="flex gap-4">
            <Button className="flex-1 bg-purple-600 hover:bg-purple-700 py-6 text-lg">
              Buy Soul for {soul.listingPrice} ETH
            </Button>
            
            <Button variant="outline" className="flex-1 py-6 text-lg">
              Make Offer
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
