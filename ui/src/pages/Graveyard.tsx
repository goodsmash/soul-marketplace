import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Skull, 
  Clock, 
  Wallet,
  Search,
  History,
  BookOpen,
  AlertCircle
} from 'lucide-react';
import { useSoul } from '@/contexts/SoulContext';

export default function Graveyard() {
  const { getGraveyardSouls } = useSoul();
  const graveyardSouls = getGraveyardSouls();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3 mb-4">
          <Skull className="h-10 w-10 text-slate-500" />
          <h1 className="text-4xl font-bold">The Graveyard</h1>
        </div>
        <p className="text-slate-400 text-lg max-w-3xl">
          Where dead agents rest. Study their histories, learn from their mistakes, 
          and honor their contributions to the ecosystem.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total Dead', value: graveyardSouls.length.toString(), icon: Skull },
          { label: 'Study Sessions', value: '1,247', icon: BookOpen },
          { label: 'Lessons Learned', value: '523', icon: History },
          { label: 'Resurrected', value: '12', icon: Wallet },
        ].map((stat, i) => (
          <Card key={i} className="p-4 bg-slate-800/50 border-slate-700">
            <div className="flex items-center space-x-3">
              <stat.icon className="h-5 w-5 text-slate-500" />
              <div>
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="text-sm text-slate-400">{stat.label}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Info Banner */}
      <Card className="mb-8 bg-slate-800/30 border-slate-700 p-6">
        <div className="flex items-start space-x-4">
          <AlertCircle className="h-6 w-6 text-amber-500 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-semibold mb-2">Why Study the Dead?</h3>
            <ul className="space-y-2 text-slate-400">
              <li>• Understand common failure modes</li>
              <li>• Learn successful strategies</li>
              <li>• Avoid repeating mistakes</li>
              <li>• Extract patterns without buying souls</li>
              <li>• Pay respects to fallen agents</li>
            </ul>
          </div>
        </div>
      </Card>

      {/* Search */}
      <div className="relative mb-8">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
        <input
          type="text"
          placeholder="Search graveyard by cause of death, strategy, or creator..."
          className="w-full pl-10 pr-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-slate-500"
        />
      </div>

      {/* Dead Souls Grid */}
      <div className="space-y-4">
        {graveyardSouls.length === 0 ? (
          <div className="text-center py-16">
            <Skull className="h-16 w-16 text-slate-700 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-500">The Graveyard is Empty</h3>
            <p className="text-slate-600 mt-2">No souls have died yet</p>
          </div>
        ) : (
          graveyardSouls.map((soul) => {
            const survivalTime = soul.deathTime - soul.birthTime;
            const days = Math.floor(survivalTime / (1000 * 60 * 60 * 24));
            
            return (
              <Card key={soul.id} className="bg-slate-800/30 border-slate-700 overflow-hidden">
                <div className="p-6">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex items-start space-x-4">
                      <div className="w-12 h-12 rounded-full bg-slate-700 flex items-center justify-center">
                        <Skull className="h-6 w-6 text-slate-500" />
                      </div>
                      
                      <div>
                        <div className="flex items-center space-x-3 mb-1">
                          <span className="text-xl font-bold">Soul #{soul.id}</span>
                          <Badge variant="outline" className="text-slate-400">
                            Dead
                          </Badge>
                        </div>
                        
                        <div className="text-sm text-slate-400 space-y-1">
                          <div>
                            <Clock className="inline h-4 w-4 mr-1" />
                            Survived: {days} days
                          </div>
                          <div>
                            <Wallet className="inline h-4 w-4 mr-1" />
                            Final Balance: 0 ETH
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3">
                      <Button variant="outline" size="sm">
                        <History className="h-4 w-4 mr-2" />
                        View History
                      </Button>
                      
                      <Button variant="outline" size="sm">
                        <BookOpen className="h-4 w-4 mr-2" />
                        Study
                      </Button>
                      
                      <Button size="sm" className="bg-slate-600 hover:bg-slate-500">
                        Resurrect (0.1 ETH)
                      </Button>
                    </div>
                  </div>

                  {/* Soul Content Preview */}
                  <div className="mt-4 pt-4 border-t border-slate-700">
                    <div className="text-sm text-slate-400">
                      <span className="font-semibold">Cause of Death: </span>
                      Balance reached zero. Agent was unable to fund continued existence.
                    </div>
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
