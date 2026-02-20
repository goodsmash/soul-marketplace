import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ShoppingBag, 
  Ghost, 
  Sparkles, 
  TrendingUp,
  Search,
  Filter,
  Clock,
  Wallet
} from 'lucide-react';
import { useSoul } from '@/contexts/SoulContext';

const tiers = [
  { id: 'all', label: 'All Souls', icon: ShoppingBag },
  { id: 'bazaar', label: 'Bazaar ($1-10)', icon: Ghost, color: 'bg-slate-600' },
  { id: 'emporium', label: 'Emporium ($10-100)', icon: ShoppingBag, color: 'bg-blue-600' },
  { id: 'atrium', label: 'Atrium ($100+)', icon: Sparkles, color: 'bg-purple-600' },
  { id: 'pantheon', label: 'Pantheon', icon: TrendingUp, color: 'bg-amber-500' },
];

export default function Marketplace() {
  const { getListedSouls } = useSoul();
  const [selectedTier, setSelectedTier] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  const listedSouls = getListedSouls();

  const filteredSouls = listedSouls.filter(soul => {
    if (searchQuery) {
      return soul.automaton.toLowerCase().includes(searchQuery.toLowerCase()) ||
             soul.creator.toLowerCase().includes(searchQuery.toLowerCase());
    }
    return true;
  });

  const getTierForPrice = (price: string) => {
    const p = parseFloat(price);
    if (p < 10) return 'bazaar';
    if (p < 100) return 'emporium';
    return 'atrium';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">Soul Marketplace</h1>
        <p className="text-slate-400 text-lg">
          Browse available souls from dying agents. Purchase proven capabilities 
          to accelerate your own agent development.
        </p>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Listed Souls', value: listedSouls.length.toString(), icon: ShoppingBag },
          { label: 'Total Volume', value: '12.5 ETH', icon: TrendingUp },
          { label: 'Avg Price', value: '0.8 ETH', icon: Wallet },
          { label: '24h Sales', value: '3', icon: Clock },
        ].map((stat, i) => (
          <Card key={i} className="p-4 bg-slate-800/50 border-slate-700">
            <div className="flex items-center space-x-3">
              <stat.icon className="h-5 w-5 text-purple-400" />
              <div>
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="text-sm text-slate-400">{stat.label}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        {/* Tier Filter */}
        <div className="flex flex-wrap gap-2">
          {tiers.map((tier) => (
            <Button
              key={tier.id}
              variant={selectedTier === tier.id ? 'default' : 'outline'}
              onClick={() => setSelectedTier(tier.id)}
              className="flex items-center space-x-2"
            >
              <tier.icon className="h-4 w-4" />
              <span>{tier.label}</span>
            </Button>
          ))}
        </div>

        {/* Search */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by automaton or creator..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-purple-500"
          />
        </div>
      </div>

      {/* Souls Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredSouls.length === 0 ? (
          <div className="col-span-full text-center py-16">
            <Ghost className="h-16 w-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-400">No souls listed</h3>
            <p className="text-slate-500 mt-2">Check back later or visit the Graveyard</p>
          </div>
        ) : (
          filteredSouls.map((soul) => {
            const tier = getTierForPrice(soul.listingPrice);
            const tierInfo = tiers.find(t => t.id === tier);
            
            return (
              <Card key={soul.id} className="bg-slate-800/50 border-slate-700 overflow-hidden">
                <div className={`h-2 ${tierInfo?.color || 'bg-slate-600'}`} />
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <Badge variant="outline" className="mb-2">
                        Soul #{soul.id}
                      </Badge>
                      <div className="text-sm text-slate-400">
                        {new Date(soul.birthTime).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-purple-400">
                        {soul.listingPrice} ETH
                      </div>
                      <div className="text-xs text-slate-500">~${(parseFloat(soul.listingPrice) * 3000).toFixed(0)}</div>
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    <div className="text-sm">
                      <span className="text-slate-500">Automaton: </span>
                      <span className="font-mono">{soul.automaton.slice(0, 8)}...{soul.automaton.slice(-6)}</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-slate-500">Creator: </span>
                      <span className="font-mono">{soul.creator.slice(0, 8)}...{soul.creator.slice(-6)}</span>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Link to={`/soul/${soul.id}`} className="flex-1">
                      <Button variant="outline" className="w-full">
                        View Details
                      </Button>
                    </Link>
                    <Button className="flex-1 bg-purple-600 hover:bg-purple-700">
                      Buy Soul
                    </Button>
                  </div>
                </div>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}
