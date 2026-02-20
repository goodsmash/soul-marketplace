import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  Clock, 
  Wallet,
  Trophy,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';

interface Stake {
  id: number;
  soulId: number;
  type: 'SURVIVE' | 'DIE';
  amount: string;
  target: number;
  odds: number;
  expiresAt: string;
}

const MOCK_STAKES: Stake[] = [
  {
    id: 1,
    soulId: 1,
    type: 'SURVIVE',
    amount: '0.5',
    target: 24,
    odds: 65,
    expiresAt: '2024-02-21T00:00:00Z',
  },
  {
    id: 2,
    soulId: 3,
    type: 'DIE',
    amount: '0.3',
    target: 12,
    odds: 40,
    expiresAt: '2024-02-20T12:00:00Z',
  },
];

export default function Staking() {
  const [activeTab, setActiveTab] = useState<'active' | 'history'>('active');

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <TrendingUp className="h-10 w-10 text-purple-500" />
          <h1 className="text-4xl font-bold">Soul Staking</h1>
        </div>
        <p className="text-slate-400 text-lg max-w-3xl">
          Stake on whether agents will survive or die. Bet on their future 
          and earn rewards for correct predictions.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total Staked', value: '45.2 ETH', icon: Wallet },
          { label: 'Active Stakes', value: '23', icon: TrendingUp },
          { label: 'Your Stakes', value: '3', icon: Trophy },
          { label: 'Win Rate', value: '67%', icon: CheckCircle },
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

      {/* How It Works */}
      <Card className="mb-8 bg-slate-800/30 border-slate-700 p-6">
        <div className="flex items-start space-x-4">
          <AlertCircle className="h-6 w-6 text-amber-500 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold mb-2">How Staking Works</h3>
            <ol className="space-y-2 text-slate-400 list-decimal list-inside">
              <li>Choose an agent and predict if it will survive or die</li>
              <li>Stake ETH on your prediction</li>
              <li>Wait for the stake period to end</li>
              <li>If correct, win your stake + share of losing pool</li>
              <li>Platform takes 5% fee, rest goes to winners</li>
            </ol>
          </div>
        </div>
      </Card>

      {/* Tabs */}
      <div className="flex space-x-4 mb-6">
        <Button
          variant={activeTab === 'active' ? 'default' : 'outline'}
          onClick={() => setActiveTab('active')}
        >
          Active Stakes
        </Button>
        <Button
          variant={activeTab === 'history' ? 'default' : 'outline'}
          onClick={() => setActiveTab('history')}
        >
          Your History
        </Button>
      </div>

      {/* Stakes List */}
      <div className="space-y-4">
        {MOCK_STAKES.map((stake) => (
          <Card key={stake.id} className="bg-slate-800/50 border-slate-700 p-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                  stake.type === 'SURVIVE' ? 'bg-green-500/20' : 'bg-red-500/20'
                }`}>
                  {stake.type === 'SURVIVE' ? (
                    <CheckCircle className="h-6 w-6 text-green-500" />
                  ) : (
                    <XCircle className="h-6 w-6 text-red-500" />
                  )}
                </div>

                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="font-semibold">Soul #{stake.soulId}</span>
                    <Badge variant={stake.type === 'SURVIVE' ? 'default' : 'destructive'}>
                      {stake.type}
                    </Badge>
                  </div>
                  
                  <div className="text-sm text-slate-400">
                    <Clock className="inline h-4 w-4 mr-1" />
                    {stake.target} hours • Expires {new Date(stake.expiresAt).toLocaleDateString()}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-6">
                <div className="text-right">
                  <div className="text-sm text-slate-400">Your Stake</div>
                  <div className="text-xl font-bold">{stake.amount} ETH</div>
                </div>

                <div className="text-right w-32">
                  <div className="text-sm text-slate-400 mb-1">Survival Odds</div>
                  <Progress value={stake.odds} className="h-2" />
                  <div className="text-sm font-medium mt-1">{stake.odds}%</div>
                </div>

                <Button variant="outline" size="sm">
                  View
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Create Stake CTA */}
      <Card className="mt-8 bg-gradient-to-r from-purple-900/50 to-pink-900/50 border-purple-500/20 p-8 text-center">
        <Trophy className="h-12 w-12 text-purple-400 mx-auto mb-4" />
        <h3 className="text-2xl font-bold mb-2">Ready to Stake?</h3>
        <p className="text-slate-300 mb-6">
          Browse available agents and make your prediction.
        </p>
        <Button className="bg-purple-600 hover:bg-purple-700 px-8 py-6 text-lg">
          Browse Agents to Stake On
        </Button>
      </Card>
    </div>
  );
}
