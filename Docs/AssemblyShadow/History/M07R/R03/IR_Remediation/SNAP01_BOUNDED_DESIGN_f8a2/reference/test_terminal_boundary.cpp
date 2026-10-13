#include "terminal_boundary.h"
#include <cassert>
#include <cstdio>
#include <thread>
#include <vector>
using namespace r03_boundary;
static Digest Key(unsigned char c) { Digest d{}; d.fill(c); return d; }
static void Ready(Coordinator& c) {
    assert(c.Prepare(Key(1), 100)); assert(c.MayScheduleManaged());
    assert(c.Request(13, 9, 1000)); assert(!c.MayScheduleManaged());
    assert(!c.Request(21, 8, 999)); assert(c.FirstCause() == 13);
}
static void Ack(Coordinator& c) {
    assert(c.Acknowledge(Key(1), 9, 42, 0, MaintenanceRequired, 1100));
    assert(c.Pulse(Key(1), 42, 1, MaintenanceRequired, 1200));
    assert(c.Pulse(Key(1), 42, 2, MaintenanceRequired, 1000 + WindowNs));
}
int main() {
    int scenarios = 0;
    { Coordinator c; assert(!c.MayScheduleManaged()); assert(!c.Request(13, 1, 0));
      assert(!c.Prepare(Key(0), 0)); ++scenarios; }
    { Coordinator c; Ready(c); Ack(c); assert(c.Sample(101));
      assert(c.Evaluate(Key(1), 1000+WindowNs, Key(3), true)==Verdict::ReadyForRestart);
      assert(!c.MayScheduleManaged());
      assert(c.BindRestart(42,43,Key(1),Key(2))); assert(!c.BindRestart(42,42,Key(1),Key(2)));
      assert(!c.BindRestart(42,43,Key(1),Key(1))); ++scenarios; }
    { Coordinator c; Ready(c); assert(c.Sample(101));
      assert(c.Evaluate(Key(1), 499999999, Key(3), true)==Verdict::Pending); ++scenarios; }
    { Coordinator c; Ready(c); assert(c.Sample(101));
      assert(c.Evaluate(Key(1), 1000+WindowNs, Key(3), true)==Verdict::Failed); ++scenarios; }
    for (unsigned which=0; which<5; ++which) {
        Coordinator c; Ready(c);
        assert(!c.Acknowledge(Key(which==0 ? 2 : 1), which==1 ? 8 : 9,
            which==2 ? 0 : 42, which==3 ? 1 : 0, which==4 ? 7 : MaintenanceRequired, 1100));
        assert(c.State()==Phase::Failed); ++scenarios;
    }
    for (unsigned reports : {0u,65u,51213u}) {
        Coordinator c; Ready(c); Ack(c); assert(c.Sample(100+reports));
        assert(c.ReportsObserved()==reports);
        assert(c.Evaluate(Key(1),1000+WindowNs,Key(3),true)==Verdict::Failed); ++scenarios;
    }
    { Coordinator c; Ready(c); Ack(c); assert(c.Sample(164));
      assert(c.Evaluate(Key(1),1000+WindowNs,Key(3),true)==Verdict::ReadyForRestart); ++scenarios; }
    { Coordinator c; Ready(c); assert(c.Sample(101)); assert(!c.Sample(100)); ++scenarios; }
    { Coordinator c; Ready(c); c.RecordLateManagedDispatch();
      assert(!c.Acknowledge(Key(1),9,42,0,MaintenanceRequired,1100)); ++scenarios; }
    { Coordinator c; Ready(c); Ack(c); c.RecordLateManagedDispatch(); assert(c.Sample(101));
      assert(c.Evaluate(Key(1),1000+WindowNs,Key(3),true)==Verdict::Failed); ++scenarios; }
    for (unsigned which=0; which<2; ++which) {
        Coordinator c; Ready(c); Ack(c); assert(c.Sample(101));
        assert(c.Evaluate(Key(1),1000+WindowNs,Key(which ? 0 : 3),which!=0)==Verdict::Failed); ++scenarios;
    }
    { Coordinator c; Ready(c); assert(c.Acknowledge(Key(1),9,42,0,MaintenanceRequired,1100));
      assert(!c.Pulse(Key(1),42,2,MaintenanceRequired,1200)); ++scenarios; }
    { Coordinator c; Ready(c); assert(c.Acknowledge(Key(1),9,42,0,MaintenanceRequired,1100));
      assert(!c.Pulse(Key(1),42,1,MaintenanceRequired,1099)); ++scenarios; }
    { Coordinator c; assert(c.Prepare(Key(1),0)); std::atomic<int> wins{0};
      std::vector<std::thread> threads;
      for(int i=0;i<16;++i) threads.emplace_back([&c,&wins,i]{if(c.Request(13+i,9,1000))++wins;});
      for(auto& t:threads)t.join(); assert(wins==1); const auto cause=c.FirstCause();
      assert(cause>=13 && cause<29); assert(!c.Request(99,10,1001));
      assert(c.FirstCause()==cause); ++scenarios; }
    std::printf("{\"scenarios\":%d,\"passed\":true,\"engineAdapterInstalled\":false}\n",scenarios);
}
